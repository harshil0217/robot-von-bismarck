import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Avatar,
  Divider
} from '@mui/material';
import { CountryResponse, COUNTRIES } from '../../types/simulation';

interface ChatConversationProps {
  geopoliticalEvent: string;
  responses: CountryResponse[];
  currentIteration: number;
}

interface ChatMessage {
  type: 'event' | 'country';
  content: string;
  country?: string;
  iteration?: number;
  timestamp?: Date;
}

export const ChatConversation: React.FC<ChatConversationProps> = ({
  geopoliticalEvent,
  responses,
  currentIteration
}) => {
  // Create conversation flow: event first, then responses in chronological order
  const createConversationFlow = (): ChatMessage[] => {
    const messages: ChatMessage[] = [];

    // Add initial geopolitical event
    if (geopoliticalEvent) {
      messages.push({
        type: 'event',
        content: geopoliticalEvent
      });
    }

    // Get unique responses (one per country per iteration)
    const uniqueResponses = responses.reduce((acc, response) => {
      const key = `${response.country}-${response.iteration}`;
      if (!acc[key] || acc[key].timestamp < response.timestamp) {
        acc[key] = response;
      }
      return acc;
    }, {} as Record<string, CountryResponse>);

    // Sort by iteration then by country order
    const sortedResponses = Object.values(uniqueResponses).sort((a, b) => {
      if (a.iteration !== b.iteration) {
        return a.iteration - b.iteration;
      }
      // Sort by country order: USA, China, Russia, EU
      const countryOrder = ['USA', 'China', 'Russia', 'EU'];
      return countryOrder.indexOf(a.country) - countryOrder.indexOf(b.country);
    });

    // Add country responses
    sortedResponses.forEach(response => {
      messages.push({
        type: 'country',
        content: response.message,
        country: response.country,
        iteration: response.iteration,
        timestamp: response.timestamp
      });
    });

    return messages;
  };

  const conversationFlow = createConversationFlow();

  const getCountryInfo = (countryName: string) => {
    return COUNTRIES.find(c => c.name === countryName);
  };

  const formatMessage = (message: string) => {
    // Remove the country prefix if it exists (e.g., "[USA] said: ...")
    return message.replace(/^\[.*?\]\s*(said:\s*)?/i, '');
  };

  const getFlagImage = (country: string) => {
    return `/flags/${country}.png`;
  };


  if (!geopoliticalEvent) {
    return (
      <Box sx={{ textAlign: 'center', py: 8, color: 'text.secondary' }}>
        <Typography variant="h6">
          Enter a geopolitical event to start the simulation
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 3 }}>
        Simulation Conversation
      </Typography>

      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 2,
        maxHeight: 600,
        overflow: 'auto',
        pr: 1
      }}>
        {conversationFlow.map((message, index) => (
          <Box key={index}>
            {message.type === 'event' ? (
              // Geopolitical Event Message
              <Paper 
                elevation={3}
                sx={{ 
                  p: 3, 
                  bgcolor: 'primary.main', 
                  color: 'primary.contrastText',
                  borderRadius: 2
                }}
              >
                <Typography variant="subtitle2" sx={{ mb: 1, opacity: 0.9 }}>
                  GEOPOLITICAL EVENT
                </Typography>
                <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
                  {message.content}
                </Typography>
              </Paper>
            ) : (
              // Country Response Message
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                <Avatar
                  src={getFlagImage(message.country!)}
                  sx={{
                    width: 56,
                    height: 56,
                    border: `3px solid ${getCountryInfo(message.country!)?.color}`,
                    mt: 1,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                  }}
                >
                  <Box
                    sx={{
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '11px',
                      fontWeight: '600',
                      color: 'white',
                      textShadow: '1px 1px 3px rgba(0,0,0,0.9), 0 0 6px rgba(0,0,0,0.5)',
                      zIndex: 2,
                      position: 'relative',
                      letterSpacing: '0.5px'
                    }}
                  >
                    {message.country!}
                  </Box>
                </Avatar>
                
                <Paper 
                  elevation={1}
                  sx={{ 
                    flex: 1,
                    p: 2,
                    borderRadius: 2,
                    bgcolor: 'background.paper',
                    border: `1px solid ${getCountryInfo(message.country!)?.color}20`
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography 
                      variant="subtitle1" 
                      sx={{ 
                        color: getCountryInfo(message.country!)?.color,
                        fontWeight: 600
                      }}
                    >
                      {message.country}
                    </Typography>
                    {message.iteration && (
                      <Typography variant="caption" color="text.secondary">
                        • Round {message.iteration}
                      </Typography>
                    )}
                    {message.timestamp && (
                      <Typography variant="caption" color="text.secondary">
                        • {message.timestamp.toLocaleTimeString()}
                      </Typography>
                    )}
                  </Box>
                  
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      lineHeight: 1.6,
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    {formatMessage(message.content)}
                  </Typography>
                </Paper>
              </Box>
            )}
            
            {index < conversationFlow.length - 1 && (
              <Divider sx={{ my: 1, opacity: 0.3 }} />
            )}
          </Box>
        ))}
        
        {responses.length > 0 && (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="caption" color="text.secondary">
              {responses.length} responses • Round {currentIteration}
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
};