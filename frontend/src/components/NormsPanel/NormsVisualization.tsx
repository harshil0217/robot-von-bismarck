import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Tooltip,
  IconButton,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Cell } from 'recharts';
import { CountryNorms, NormValues, COUNTRIES, NORM_DEFINITIONS } from '../../types/simulation';

interface NormsVisualizationProps {
  currentNorms: CountryNorms;
  initialNorms: CountryNorms;
  showComparison?: boolean;
}

export const NormsVisualization: React.FC<NormsVisualizationProps> = ({
  currentNorms,
  initialNorms,
  showComparison = true
}) => {
  const [selectedCountry, setSelectedCountry] = useState(0);
  const [showInitialValues, setShowInitialValues] = useState(false);

  const selectedCountryName = COUNTRIES[selectedCountry].name;
  const selectedCountryColor = COUNTRIES[selectedCountry].color;

  const formatNormData = (norms: NormValues) => {
    return Object.entries(norms).map(([key, value]) => ({
      name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: value,
      fullName: key as keyof NormValues
    }));
  };

  const currentNormData = formatNormData(currentNorms[selectedCountryName] || {});
  const initialNormData = formatNormData(initialNorms[selectedCountryName] || {});

  const getBarColor = (value: number) => {
    if (value > 0.5) return '#4caf50'; // Green for positive
    if (value < -0.5) return '#f44336'; // Red for negative
    return '#ff9800'; // Orange for neutral
  };

  const calculateChange = (current: number, initial: number) => {
    const change = current - initial;
    return {
      value: change,
      percentage: initial !== 0 ? (change / Math.abs(initial)) * 100 : 0,
      isIncrease: change > 0,
      isDecrease: change < 0
    };
  };

  return (
    <Paper elevation={0} sx={{ p: 2, height: '100%', backgroundColor: '#1a1a1a', m: 0 }}>
      <Typography variant="h5" component="h2" gutterBottom sx={{ color: '#ffffff', fontFamily: 'Verdana, sans-serif' }}>
        Ideological Norms
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: '#333333', mb: 1 }}>
        <Tabs
          value={selectedCountry}
          onChange={(_, newValue) => setSelectedCountry(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              color: '#cccccc',
              fontFamily: 'Verdana, sans-serif',
            },
            '& .Mui-selected': {
              color: '#ffffff',
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#90caf9',
            },
          }}
        >
          {COUNTRIES.map((country, index) => (
            <Tab
              key={country.name}
              label={`${country.flag} ${country.name}`}
              sx={{ color: country.color }}
            />
          ))}
        </Tabs>
      </Box>

      {showComparison && (
        <FormControlLabel
          control={
            <Switch
              checked={showInitialValues}
              onChange={(e) => setShowInitialValues(e.target.checked)}
              size="small"
            />
          }
          label="Show initial values"
          sx={{ mb: 2 }}
        />
      )}

      <Box sx={{ height: 400, mb: 3 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={currentNormData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="name" 
              angle={-45}
              textAnchor="end"
              height={100}
              fontSize={10}
            />
            <YAxis domain={[-1, 1]} />
            <Bar dataKey="value" name="Current Value">
              {currentNormData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(entry.value)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>

      <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
        {Object.entries(NORM_DEFINITIONS).map(([normKey, definition]) => {
          const currentValue = currentNorms[selectedCountryName]?.[normKey as keyof NormValues] || 0;
          const initialValue = initialNorms[selectedCountryName]?.[normKey as keyof NormValues] || 0;
          const change = calculateChange(currentValue, initialValue);

          return (
            <Accordion key={normKey} sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
                  <Typography variant="subtitle2" sx={{ flex: 1 }}>
                    {normKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </Typography>
                  <Tooltip title={definition}>
                    <IconButton size="small">
                      <InfoIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontWeight: 'bold',
                      color: getBarColor(currentValue),
                      minWidth: 40,
                      textAlign: 'right'
                    }}
                  >
                    {currentValue.toFixed(2)}
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box>
                  <Typography variant="body2" color="textSecondary" paragraph>
                    {definition}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" display="block" gutterBottom>
                      Current: {currentValue.toFixed(2)}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={((currentValue + 1) / 2) * 100}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: getBarColor(currentValue)
                        }
                      }}
                    />
                  </Box>

                  {showComparison && showInitialValues && Math.abs(change.value) > 0.001 && (
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Change from initial: 
                        <span style={{ 
                          color: change.isIncrease ? '#4caf50' : '#f44336',
                          fontWeight: 'bold',
                          marginLeft: 4
                        }}>
                          {change.isIncrease ? '+' : ''}{change.value.toFixed(3)}
                        </span>
                      </Typography>
                    </Box>
                  )}
                </Box>
              </AccordionDetails>
            </Accordion>
          );
        })}
      </Box>
    </Paper>
  );
};