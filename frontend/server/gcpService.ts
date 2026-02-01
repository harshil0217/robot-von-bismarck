import { execSync } from 'child_process';

const GCP_BASE_ENDPOINT = 'https://us-central1-aiplatform.googleapis.com/v1/projects/gen-lang-client-0834462342/locations/us-central1/reasoningEngines/8173748550165856256';

export class GcpReasoningEngine {
  private cachedToken: string | null = null;
  private tokenExpiry: number | null = null;

  /**
   * Get fresh access token (cached for 58 minutes)
   */
  private async getToken(): Promise<string> {
    // Return cached if still valid
    if (this.cachedToken && this.tokenExpiry && Date.now() < this.tokenExpiry) {
      console.log('Using cached GCP token');
      return this.cachedToken;
    }

    try {
      // Get new token from gcloud
      console.log('Fetching new GCP access token...');
      this.cachedToken = execSync('gcloud auth print-access-token', {
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'pipe']
      }).trim();

      // Cache for 58 minutes (tokens last 60)
      this.tokenExpiry = Date.now() + (58 * 60 * 1000);

      console.log('✓ Refreshed GCP access token (valid for 58 minutes)');
      return this.cachedToken;
    } catch (error: any) {
      console.error('Failed to get gcloud token:', error.message);
      throw new Error('Failed to get gcloud token. Run: gcloud auth login');
    }
  }

  /**
   * Create a new session
   */
  private async createSession(token: string, userId: string): Promise<string> {
    console.log('Creating GCP session for user:', userId);

    const response = await fetch(`${GCP_BASE_ENDPOINT}:query`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        class_method: 'async_create_session',
        input: {
          user_id: userId
        }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to create session (${response.status}): ${errorText}`);
    }

    const result: any = await response.json();
    const sessionId = result.output?.id || result.id;
    console.log('✓ Created session:', sessionId);

    return sessionId;
  }

  /**
   * Delete a session
   */
  private async deleteSession(token: string, sessionId: string, userId: string): Promise<void> {
    console.log('Deleting session:', sessionId);

    try {
      const response = await fetch(`${GCP_BASE_ENDPOINT}:query`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          class_method: 'async_delete_session',
          input: {
            user_id: userId,
            session_id: sessionId
          }
        })
      });

      if (!response.ok) {
        console.warn('Failed to delete session (non-critical):', response.status);
      } else {
        console.log('✓ Deleted session');
      }
    } catch (error) {
      console.warn('Failed to delete session (non-critical):', error);
    }
  }

  /**
   * Query the reasoning engine using session-based API
   */
  async query(input: string): Promise<any> {
    const token = await this.getToken();
    const userId = 'user_' + Date.now();
    let sessionId: string | null = null;

    console.log('Calling GCP Reasoning Engine...');
    console.log('Input:', input.substring(0, 100) + '...');

    const controller = new AbortController();
    const timeout = setTimeout(() => {
      console.error('Request timeout after 5 minutes');
      controller.abort();
    }, 300000); // 5 min

    try {
      // Step 1: Create session
      sessionId = await this.createSession(token, userId);

      // Step 2: Query with session using async_stream_query
      console.log('Querying with session...');
      const response = await fetch(`${GCP_BASE_ENDPOINT}:query`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          class_method: 'async_stream_query',
          input: {
            user_id: userId,
            session_id: sessionId,
            message: input
          }
        }),
        signal: controller.signal
      });

      clearTimeout(timeout);

      console.log('GCP Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('GCP API error:', errorText);

        if (response.status === 401) {
          // Token expired, clear cache and retry once
          console.log('Token expired, refreshing and retrying...');
          this.cachedToken = null;
          this.tokenExpiry = null;

          // Retry once with fresh token
          return this.query(input);
        }

        if (response.status === 403) {
          throw new Error('Permission denied. Check IAM roles for Reasoning Engine.');
        }

        if (response.status === 404) {
          throw new Error('Reasoning Engine not found. Check endpoint URL.');
        }

        throw new Error(`GCP API error (${response.status}): ${errorText}`);
      }

      const result = await response.json();
      console.log('✓ Received response from GCP');

      // Step 3: Clean up session
      if (sessionId) {
        await this.deleteSession(token, sessionId, userId);
      }

      return result;
    } catch (error: any) {
      clearTimeout(timeout);

      // Clean up session on error
      if (sessionId) {
        await this.deleteSession(token, sessionId, userId);
      }

      if (error.name === 'AbortError') {
        throw new Error('Request timeout after 5 minutes');
      }

      if (error.code === 'ENOTFOUND') {
        throw new Error('No internet connection or GCP endpoint unreachable');
      }

      throw error;
    }
  }

  /**
   * Check if gcloud is installed and authenticated
   */
  async healthCheck(): Promise<{ healthy: boolean; message: string }> {
    // Check gcloud installation
    try {
      execSync('gcloud --version', {
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'pipe']
      });
    } catch (error) {
      return {
        healthy: false,
        message: 'gcloud CLI not installed. Install from cloud.google.com/sdk/docs/install'
      };
    }

    // Check authentication
    try {
      await this.getToken();
      return {
        healthy: true,
        message: 'GCP connection ready'
      };
    } catch (error: any) {
      return {
        healthy: false,
        message: 'Not authenticated with gcloud. Run: gcloud auth login'
      };
    }
  }
}

export const gcpService = new GcpReasoningEngine();
