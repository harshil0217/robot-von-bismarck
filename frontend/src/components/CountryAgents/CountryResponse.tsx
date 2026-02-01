import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Chip
} from '@mui/material';
import { CountryResponse as CountryResponseType, Country } from '../../types/simulation';

interface CountryResponseProps {
  response: CountryResponseType;
  country: Country;
  isLatest?: boolean;
}

export const CountryResponse: React.FC<CountryResponseProps> = ({
  response,
  country,
  isLatest = false
}) => {
  const formatMessage = (message: string) => {
    // Remove the country prefix if it exists (e.g., "[USA] said: ...")
    const cleanMessage = message.replace(/^\[.*?\]\s*(said:\s*)?/i, '');
    return cleanMessage;
  };

  return (
    <Card
      elevation={0}
      sx={{
        mb: 1,
        backgroundColor: '#1a1a1a',
        border: isLatest ? `2px solid ${country.color}` : '1px solid #333333',
        transition: 'all 0.3s ease-in-out',
        opacity: isLatest ? 1 : 0.85
      }}
    >
      <CardContent sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
          <Avatar
            sx={{
              bgcolor: country.color,
              width: 48,
              height: 48,
              fontSize: '1.5rem',
              mr: 2
            }}
          >
            {country.flag}
          </Avatar>

          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <Typography variant="h6" component="h3" sx={{ color: country.color, fontFamily: 'Verdana, sans-serif' }}>
                {country.name}
              </Typography>
              <Chip
                label={`Round ${response.iteration}`}
                size="small"
                variant="outlined"
                sx={{
                  borderColor: country.color,
                  color: country.color,
                  fontFamily: 'Verdana, sans-serif'
                }}
              />
            </Box>

            <Typography variant="caption" sx={{ mb: 0.5, display: 'block', color: '#888888', fontFamily: 'Verdana, sans-serif' }}>
              {response.timestamp.toLocaleTimeString()}
            </Typography>
          </Box>
        </Box>

        <Typography
          variant="body1"
          sx={{
            lineHeight: 1.6,
            whiteSpace: 'pre-wrap',
            color: '#ffffff',
            fontFamily: 'Verdana, sans-serif',
            '& p': { margin: 0, marginBottom: 0.5 }
          }}
        >
          {formatMessage(response.message)}
        </Typography>
      </CardContent>
    </Card>
  );
};