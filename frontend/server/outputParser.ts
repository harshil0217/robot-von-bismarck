// ADK output parser - handles country responses and analyst JSON

import { CountryResponse, AnalystResponse } from './types';

export class OutputParser {
  private jsonBuffer: string = '';
  private inJsonBlock: boolean = false;
  private currentResponse: Partial<CountryResponse> | null = null;
  private currentIteration: number = 1;

  // Country name pattern matching
  private readonly COUNTRY_PATTERN = /\[(USA|China|Russia|EU)\]/i;

  // Detect "said:" pattern if present
  private readonly SAID_PATTERN = /\[(USA|China|Russia|EU)\]\s*said:\s*(.*)/i;

  /**
   * Parse a single line of ADK output
   * Returns parsed message or null if line should be accumulated
   */
  parseLine(line: string): CountryResponse | AnalystResponse | null {
    const trimmedLine = line.trim();

    // Skip empty lines
    if (!trimmedLine) {
      return null;
    }

    // Try parsing as analyst JSON
    const analystResponse = this.tryParseAnalystJson(trimmedLine);
    if (analystResponse) {
      this.currentIteration = analystResponse.iteration;
      return analystResponse;
    }

    // Try parsing as country response
    const countryResponse = this.tryParseCountryResponse(line);
    if (countryResponse) {
      return countryResponse;
    }

    return null;
  }

  /**
   * Try to parse line as analyst JSON
   */
  private tryParseAnalystJson(line: string): AnalystResponse | null {
    // Detect JSON start
    if (line.startsWith('{') && !this.inJsonBlock) {
      this.inJsonBlock = true;
      this.jsonBuffer = line;
      return null;
    }

    // Accumulate JSON lines
    if (this.inJsonBlock) {
      this.jsonBuffer += '\n' + line;

      // Check if we have matching braces
      const openBraces = (this.jsonBuffer.match(/{/g) || []).length;
      const closeBraces = (this.jsonBuffer.match(/}/g) || []).length;

      if (openBraces > 0 && openBraces === closeBraces) {
        try {
          const parsed = JSON.parse(this.jsonBuffer);

          // Validate it's an analyst response
          if (
            parsed.iteration !== undefined &&
            parsed.analysis &&
            parsed.norm_updates &&
            parsed.reasoning
          ) {
            this.inJsonBlock = false;
            this.jsonBuffer = '';
            return parsed as AnalystResponse;
          }
        } catch (e) {
          console.error('Failed to parse JSON:', e);
          console.error('Buffer:', this.jsonBuffer);
          // Reset on parse error
          this.inJsonBlock = false;
          this.jsonBuffer = '';
        }
      }
    }

    return null;
  }

  /**
   * Try to parse line as country response
   * Handles multi-line responses by accumulating
   */
  private tryParseCountryResponse(line: string): CountryResponse | null {
    // Check for country marker at start of line
    const countryMatch = line.match(this.COUNTRY_PATTERN);

    if (countryMatch) {
      // New country response starting
      const completedResponse = this.currentResponse
        ? { ...this.currentResponse } as CountryResponse
        : null;

      // Check for "said:" pattern
      const saidMatch = line.match(this.SAID_PATTERN);
      const message = saidMatch
        ? saidMatch[2].trim()
        : line.replace(this.COUNTRY_PATTERN, '').trim();

      // Start new response
      this.currentResponse = {
        country: this.normalizeCountryName(countryMatch[1]),
        message: message,
        iteration: this.currentIteration,
        timestamp: new Date()
      };

      return completedResponse;
    } else if (this.currentResponse && line.trim() && !this.inJsonBlock) {
      // Continuation of current country response
      // Skip system messages and ADK output
      if (!this.isSystemMessage(line)) {
        this.currentResponse.message += '\n' + line.trim();
      }
    }

    return null;
  }

  /**
   * Normalize country name variations
   */
  private normalizeCountryName(name: string): 'USA' | 'China' | 'Russia' | 'EU' {
    const normalized = name.toLowerCase();

    if (normalized === 'usa' || normalized === 'us' || normalized === 'united states') {
      return 'USA';
    }
    if (normalized === 'china' || normalized === 'prc') {
      return 'China';
    }
    if (normalized === 'russia' || normalized === 'russian federation') {
      return 'Russia';
    }
    if (normalized === 'eu' || normalized === 'european union') {
      return 'EU';
    }

    return name as any; // Fallback
  }

  /**
   * Check if line is a system message to skip
   */
  private isSystemMessage(line: string): boolean {
    const systemPatterns = [
      /^Running agent/i,
      /^type exit to exit/i,
      /^\[user\]:/i,
      /^\[system\]:/i,
      /^Session/i,
      /^Iteration/i,
    ];

    return systemPatterns.some(pattern => pattern.test(line));
  }

  /**
   * Finalize and return any pending country response
   */
  finalize(): CountryResponse | null {
    if (this.currentResponse) {
      const response = { ...this.currentResponse } as CountryResponse;
      this.currentResponse = null;
      return response;
    }
    return null;
  }

  /**
   * Reset parser state
   */
  reset() {
    this.jsonBuffer = '';
    this.inJsonBlock = false;
    this.currentResponse = null;
    this.currentIteration = 1;
  }

  /**
   * Get current iteration
   */
  getCurrentIteration(): number {
    return this.currentIteration;
  }
}
