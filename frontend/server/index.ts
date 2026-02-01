// Express server with GCP Reasoning Engine integration

import express from 'express';
import cors from 'cors';
import * as path from 'path';
import { gcpService } from './gcpService';
import { OutputParser } from './outputParser';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors({ origin: 'http://localhost:3000' }));
app.use(express.json());

// Serve static files from React build (production)
const buildPath = path.join(__dirname, '..', 'build');
app.use(express.static(buildPath));

// Health check endpoint
app.get('/api/health', async (req, res) => {
  try {
    const health = await gcpService.healthCheck();
    res.json(health);
  } catch (error: any) {
    res.status(500).json({
      healthy: false,
      message: error.message
    });
  }
});

// Start simulation endpoint
app.post('/api/simulate', async (req, res) => {
  const { event, initialNorms } = req.body;

  if (!event || typeof event !== 'string') {
    return res.status(400).json({
      success: false,
      error: 'Event is required and must be a string'
    });
  }

  try {
    console.log('\n=================================');
    console.log('Starting simulation');
    console.log('Event:', event);
    console.log('=================================\n');

    // Call GCP Reasoning Engine
    const result = await gcpService.query(event);

    console.log('\nRaw GCP Result:');
    console.log(JSON.stringify(result, null, 2));

    // Parse the response
    const parsed = parseGcpOutput(result);

    console.log('\nParsed Results:');
    console.log('- Country responses:', parsed.countryResponses.length);
    console.log('- Analyst responses:', parsed.analystResponses.length);
    console.log('=================================\n');

    res.json({
      success: true,
      responses: parsed
    });
  } catch (error: any) {
    console.error('\n✗ Simulation error:', error.message);
    console.error('Stack:', error.stack);

    res.status(500).json({
      success: false,
      error: error.message || 'Unknown error occurred'
    });
  }
});

/**
 * Parse GCP Reasoning Engine output
 */
function parseGcpOutput(result: any) {
  const parser = new OutputParser();
  const countryResponses: any[] = [];
  const analystResponses: any[] = [];

  // Extract output from GCP response
  // Possible formats: result.output, result.response, or entire result
  let output: string;

  if (typeof result === 'string') {
    output = result;
  } else if (result.output) {
    output = typeof result.output === 'string' ? result.output : JSON.stringify(result.output);
  } else if (result.response) {
    output = typeof result.response === 'string' ? result.response : JSON.stringify(result.response);
  } else {
    output = JSON.stringify(result);
  }

  console.log('\nParsing output (' + output.length + ' chars)...');

  // Parse line by line
  const lines = output.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) continue;

    try {
      const parsed = parser.parseLine(line);

      if (parsed) {
        if ('country' in parsed) {
          console.log(`  ✓ Found country response: ${parsed.country} (iteration ${parsed.iteration})`);
          countryResponses.push(parsed);
        } else if ('iteration' in parsed && 'norm_updates' in parsed) {
          console.log(`  ✓ Found analyst response for iteration ${parsed.iteration}`);
          analystResponses.push(parsed);
        }
      }
    } catch (error: any) {
      console.warn(`  ! Failed to parse line ${i}:`, line.substring(0, 50));
    }
  }

  // Finalize parser (get any pending country response)
  const finalResponse = parser.finalize();
  if (finalResponse) {
    console.log(`  ✓ Found final country response: ${finalResponse.country}`);
    countryResponses.push(finalResponse);
  }

  // If no parsed responses, maybe output is already structured JSON
  if (countryResponses.length === 0 && analystResponses.length === 0) {
    console.log('  ! No responses parsed from lines, checking for structured data...');

    try {
      // Try parsing entire output as JSON
      const jsonOutput = JSON.parse(output);

      if (jsonOutput.country_responses) {
        countryResponses.push(...jsonOutput.country_responses);
      }
      if (jsonOutput.analyst_responses) {
        analystResponses.push(...jsonOutput.analyst_responses);
      }
    } catch (e) {
      console.warn('  ! Output is not valid JSON either');
    }
  }

  return {
    countryResponses,
    analystResponses
  };
}

// Catch-all handler for React routes (only in production)
if (process.env.NODE_ENV === 'production') {
  app.get('/*', (req, res) => {
    res.sendFile(path.join(buildPath, 'index.html'));
  });
}

// Start server
app.listen(PORT, async () => {
  console.log('=================================');
  console.log(`Server running on port ${PORT}`);
  console.log('=================================\n');

  // Check GCP connection on startup
  console.log('Checking GCP Reasoning Engine connection...');
  const health = await gcpService.healthCheck();

  if (health.healthy) {
    console.log('✓', health.message);
    console.log('\n✓ Ready to accept simulation requests!\n');
  } else {
    console.error('✗', health.message);
    console.error('\n⚠ GCP connection not ready. Fix before running simulations.\n');
  }

  console.log('=================================');
  console.log('Endpoints:');
  console.log('  GET  /api/health   - Check GCP connection');
  console.log('  POST /api/simulate - Start simulation');
  console.log('=================================\n');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('\nSIGTERM signal received: closing HTTP server');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('\nSIGINT signal received: closing HTTP server');
  process.exit(0);
});
