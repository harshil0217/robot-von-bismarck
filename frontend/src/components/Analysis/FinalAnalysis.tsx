import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Visibility as VisibilityIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import { AnalystResponse, COUNTRIES } from '../../types/simulation';

interface FinalAnalysisProps {
  analystResponses: AnalystResponse[];
}

export const FinalAnalysis: React.FC<FinalAnalysisProps> = ({
  analystResponses
}) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalystResponse | null>(null);

  if (analystResponses.length === 0) {
    return (
      <Paper elevation={0} sx={{ p: 2, backgroundColor: '#1a1a1a', m: 0 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <AnalyticsIcon sx={{ color: '#90caf9' }} />
          <Typography variant="h5" component="h2" sx={{ color: '#ffffff', fontFamily: 'Verdana, sans-serif' }}>
            Analysis
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ fontStyle: 'italic', color: '#888888', fontFamily: 'Verdana, sans-serif' }}>
          Analysis will appear after each round of country responses...
        </Typography>
      </Paper>
    );
  }

  const latestAnalysis = analystResponses[analystResponses.length - 1];

  const handleOpenDialog = (analysis: AnalystResponse) => {
    setSelectedAnalysis(analysis);
    setOpenDialog(true);
  };

  return (
    <>
      <Paper elevation={0} sx={{ p: 2, backgroundColor: '#1a1a1a', m: 0 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <AnalyticsIcon sx={{ color: '#90caf9' }} />
          <Typography variant="h5" component="h2" sx={{ color: '#ffffff', fontFamily: 'Verdana, sans-serif' }}>
            Analysis
          </Typography>
          <Chip
            label={`${analystResponses.length} round${analystResponses.length > 1 ? 's' : ''}`}
            size="small"
            variant="outlined"
            sx={{ borderColor: '#90caf9', color: '#90caf9', fontFamily: 'Verdana, sans-serif' }}
          />
        </Box>

        {/* Latest Analysis Summary */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" gutterBottom sx={{ color: '#ffffff', fontFamily: 'Verdana, sans-serif' }}>
            Latest Analysis (Round {latestAnalysis.iteration})
          </Typography>
          <Typography variant="body1" paragraph sx={{ lineHeight: 1.6, color: '#ffffff', fontFamily: 'Verdana, sans-serif' }}>
            {latestAnalysis.analysis}
          </Typography>
          
          <Button
            variant="outlined"
            startIcon={<VisibilityIcon />}
            onClick={() => handleOpenDialog(latestAnalysis)}
            sx={{ mr: 1 }}
          >
            View Detailed Reasoning
          </Button>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Previous Analyses */}
        {analystResponses.length > 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Previous Rounds
            </Typography>
            {analystResponses.slice(0, -1).reverse().map((analysis) => (
              <Accordion key={analysis.iteration} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1">
                      Round {analysis.iteration}
                    </Typography>
                    <Chip 
                      label="Previous"
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" paragraph>
                    {analysis.analysis}
                  </Typography>
                  <Button
                    size="small"
                    startIcon={<VisibilityIcon />}
                    onClick={() => handleOpenDialog(analysis)}
                  >
                    View Details
                  </Button>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}
      </Paper>

      {/* Detailed Analysis Dialog */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#1a1a1a',
            color: '#ffffff',
            fontFamily: 'Verdana, sans-serif',
          },
        }}
      >
        <DialogTitle sx={{ color: '#ffffff', fontFamily: 'Verdana, sans-serif' }}>
          Detailed Analysis - Round {selectedAnalysis?.iteration}
        </DialogTitle>
        <DialogContent>
          {selectedAnalysis && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Overall Analysis
              </Typography>
              <Typography variant="body1" paragraph sx={{ lineHeight: 1.6 }}>
                {selectedAnalysis.analysis}
              </Typography>

              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                Country-Specific Reasoning
              </Typography>
              
              {COUNTRIES.map(country => (
                <Box key={country.name} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Typography 
                      variant="subtitle1" 
                      sx={{ 
                        color: country.color,
                        fontWeight: 'bold'
                      }}
                    >
                      {country.flag} {country.name}
                    </Typography>
                  </Box>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      pl: 2,
                      borderLeft: `3px solid ${country.color}`,
                      lineHeight: 1.5
                    }}
                  >
                    {selectedAnalysis.reasoning[country.name] || 'No specific reasoning provided.'}
                  </Typography>
                </Box>
              ))}

              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                Norm Updates Summary
              </Typography>
              
              {COUNTRIES.map(country => {
                const countryNorms = selectedAnalysis.norm_updates[country.name];
                if (!countryNorms) return null;

                const significantChanges = Object.entries(countryNorms)
                  .filter(([_, value]) => typeof value === 'number' && Math.abs(value) > 0.1)
                  .sort(([_, a], [__, b]) => Math.abs(b as number) - Math.abs(a as number));

                return (
                  <Box key={country.name} sx={{ mb: 2 }}>
                    <Typography 
                      variant="subtitle2" 
                      sx={{ color: country.color, fontWeight: 'bold', mb: 1 }}
                    >
                      {country.flag} {country.name}
                    </Typography>
                    
                    {significantChanges.length > 0 ? (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, pl: 2 }}>
                        {significantChanges.slice(0, 3).map(([norm, value]) => (
                          <Chip
                            key={norm}
                            label={`${norm.replace(/_/g, ' ')}: ${(value as number).toFixed(2)}`}
                            size="small"
                            color={Math.abs(value as number) > 0.5 ? 'primary' : 'default'}
                            variant="outlined"
                          />
                        ))}
                        {significantChanges.length > 3 && (
                          <Chip
                            label={`+${significantChanges.length - 3} more`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    ) : (
                      <Typography variant="caption" color="textSecondary" sx={{ pl: 2 }}>
                        Minor changes across all norms
                      </Typography>
                    )}
                  </Box>
                );
              })}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};