import React from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  AppBar,
  Toolbar,
  IconButton,
  Fab
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  GitHub as GitHubIcon
} from '@mui/icons-material';

interface LayoutProps {
  children: React.ReactNode;
  onReset?: () => void;
}

export const Layout: React.FC<LayoutProps> = ({ children, onReset }) => {
  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', backgroundColor: '#000000' }}>
      <AppBar position="static" elevation={0} sx={{ backgroundColor: '#1a1a1a' }}>
        <Toolbar sx={{ minHeight: '48px !important' }}>
          <IconButton
            size="large"
            edge="end"
            color="inherit"
            aria-label="github"
            href="https://github.com"
            target="_blank"
            sx={{ color: '#ffffff', ml: 'auto' }}
          >
            <GitHubIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ p: 0, m: 0 }} disableGutters>
        {children}
      </Container>

      {onReset && (
        <Fab
          color="secondary"
          aria-label="reset"
          onClick={onReset}
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
          }}
        >
          <RefreshIcon />
        </Fab>
      )}
    </Box>
  );
};