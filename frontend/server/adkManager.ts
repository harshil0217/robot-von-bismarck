// ADK Process Manager - spawns Python ADK CLI and manages output

import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import { OutputParser } from './outputParser';
import { CountryNorms, CountryResponse, AnalystResponse } from './types';

export class AdkManager {
  private process: ChildProcess | null = null;
  private parser: OutputParser;
  private isRunning: boolean = false;
  private outputCallback?: (message: CountryResponse | AnalystResponse) => void;
  private errorCallback?: (error: Error) => void;
  private completeCallback?: () => void;
  private projectRoot: string;

  constructor() {
    this.parser = new OutputParser();
    // Project root is two directories up from server/ (frontend/server -> frontend -> project root)
    this.projectRoot = path.resolve(__dirname, '..', '..');
  }

  /**
   * Start ADK simulation
   */
  async startSimulation(
    geopoliticalEvent: string,
    initialNorms: CountryNorms,
    onOutput?: (message: CountryResponse | AnalystResponse) => void,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): Promise<void> {
    if (this.isRunning) {
      throw new Error('Simulation already running');
    }

    this.outputCallback = onOutput;
    this.errorCallback = onError;
    this.completeCallback = onComplete;
    this.parser.reset();

    try {
      // Create input JSON for ADK replay mode
      const inputJson = this.createInputJson(geopoliticalEvent, initialNorms);
      const inputPath = await this.writeInputFile(inputJson);

      // Spawn ADK process
      await this.spawnAdkProcess(inputPath);
    } catch (error) {
      this.isRunning = false;
      if (this.errorCallback) {
        this.errorCallback(error as Error);
      }
      throw error;
    }
  }

  /**
   * Create input JSON for ADK replay mode
   */
  private createInputJson(event: string, initialNorms: CountryNorms): object {
    return {
      state: {},
      queries: [event]
    };
  }

  /**
   * Write input JSON to temporary file
   */
  private async writeInputFile(inputJson: object): Promise<string> {
    const tempDir = path.join(this.projectRoot, '.temp');

    // Create temp directory if it doesn't exist
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }

    const inputPath = path.join(tempDir, `input_${Date.now()}.json`);
    fs.writeFileSync(inputPath, JSON.stringify(inputJson, null, 2));

    return inputPath;
  }

  /**
   * Spawn ADK Python process
   */
  private async spawnAdkProcess(inputPath: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const agentPath = path.join(this.projectRoot, 'international_system', 'agent.py');

      // Check if agent file exists
      if (!fs.existsSync(agentPath)) {
        reject(new Error(`Agent file not found: ${agentPath}`));
        return;
      }

      console.log('Starting ADK process...');
      console.log('Agent path:', agentPath);
      console.log('Input path:', inputPath);
      console.log('Working directory:', this.projectRoot);

      // Spawn ADK CLI process
      // Command: adk run --replay <input> <agent_path>
      this.process = spawn('adk', ['run', '--replay', inputPath, agentPath], {
        cwd: this.projectRoot,
        shell: true,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.isRunning = true;

      // Handle stdout
      this.process.stdout?.on('data', (data: Buffer) => {
        const lines = data.toString().split('\n');

        for (const line of lines) {
          if (line.trim()) {
            console.log('ADK output:', line);
            const parsed = this.parser.parseLine(line);

            if (parsed && this.outputCallback) {
              this.outputCallback(parsed);
            }
          }
        }
      });

      // Handle stderr
      this.process.stderr?.on('data', (data: Buffer) => {
        console.error('ADK stderr:', data.toString());
      });

      // Handle process exit
      this.process.on('close', (code: number | null) => {
        console.log(`ADK process exited with code ${code}`);

        // Send any final accumulated response
        const finalResponse = this.parser.finalize();
        if (finalResponse && this.outputCallback) {
          this.outputCallback(finalResponse);
        }

        this.isRunning = false;
        this.process = null;

        // Clean up input file
        try {
          fs.unlinkSync(inputPath);
        } catch (e) {
          console.error('Failed to delete input file:', e);
        }

        if (this.completeCallback) {
          this.completeCallback();
        }

        resolve();
      });

      // Handle process errors
      this.process.on('error', (error: Error) => {
        console.error('ADK process error:', error);
        this.isRunning = false;

        if (this.errorCallback) {
          this.errorCallback(error);
        }

        reject(error);
      });

      // Set timeout (5 minutes)
      setTimeout(() => {
        if (this.isRunning) {
          console.error('ADK process timeout');
          this.stopSimulation();
          reject(new Error('Simulation timeout after 5 minutes'));
        }
      }, 5 * 60 * 1000);
    });
  }

  /**
   * Stop running simulation
   */
  stopSimulation(): void {
    if (this.process) {
      console.log('Stopping ADK process...');
      this.process.kill('SIGTERM');
      this.process = null;
      this.isRunning = false;
    }
  }

  /**
   * Check if simulation is running
   */
  isSimulationRunning(): boolean {
    return this.isRunning;
  }
}
