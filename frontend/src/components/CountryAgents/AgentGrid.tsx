import React from 'react';
import {
  Typography,
  Box,
  Paper
} from '@mui/material';
import { CountryResponse } from './CountryResponse';
import { CountryResponse as CountryResponseType, COUNTRIES } from '../../types/simulation';

interface AgentGridProps {
  responses: CountryResponseType[];
  currentIteration: number;
}

export const AgentGrid: React.FC<AgentGridProps> = ({
  responses,
  currentIteration
}) => {
  // Group responses by country and iteration
  const responsesByCountry = responses.reduce((acc, response) => {
    if (!acc[response.country]) {
      acc[response.country] = [];
    }
    acc[response.country].push(response);
    return acc;
  }, {} as Record<string, CountryResponseType[]>);

  // Sort responses by timestamp for each country
  Object.keys(responsesByCountry).forEach(country => {
    responsesByCountry[country].sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  });

  return (
    <Box>
      <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
        Country Responses
      </Typography>

      <Box sx={{ 
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
        gap: 3
      }}>
        {COUNTRIES.map(country => {
          const countryResponses = responsesByCountry[country.name] || [];
          const latestResponse = countryResponses[countryResponses.length - 1];

          return (
            <Paper 
              key={country.name}
              elevation={1} 
              sx={{ 
                p: 2, 
                height: '100%',
                minHeight: 400,
                backgroundColor: `${country.color}08`
              }}
            >
              <Typography 
                variant="h6" 
                component="h3" 
                gutterBottom 
                sx={{ 
                  color: country.color,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  mb: 2
                }}
              >
                {country.flag} {country.name}
              </Typography>

              <Box sx={{ maxHeight: 350, overflow: 'auto' }}>
                {countryResponses.length === 0 ? (
                  <Typography variant="body2" color="textSecondary" sx={{ fontStyle: 'italic' }}>
                    Waiting for response...
                  </Typography>
                ) : (
                  countryResponses.map((response, index) => (
                    <CountryResponse
                      key={`${response.country}-${response.iteration}-${index}`}
                      response={response}
                      country={country}
                      isLatest={response === latestResponse && response.iteration === currentIteration}
                    />
                  ))
                )}
              </Box>
            </Paper>
          );
        })}
      </Box>
    </Box>
  );
};