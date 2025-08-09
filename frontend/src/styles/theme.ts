import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0078D4', // Microsoft Blue
      light: '#106EBE',
      dark: '#005A9E',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#5C2D91', // Microsoft Purple
      light: '#8764B8',
      dark: '#421B6A',
      contrastText: '#ffffff',
    },
    error: {
      main: '#D13438', // Microsoft Red
    },
    warning: {
      main: '#FFB900', // Microsoft Yellow
    },
    info: {
      main: '#0078D4',
    },
    success: {
      main: '#107C10', // Microsoft Green
    },
    background: {
      default: '#F3F2F1', // Microsoft Light Gray
      paper: '#FFFFFF',
    },
    grey: {
      50: '#FAF9F8',
      100: '#F3F2F1',
      200: '#EDEBE9',
      300: '#E1DFDD',
      400: '#D2D0CE',
      500: '#A19F9D',
      600: '#605E5C',
      700: '#3B3A39',
      800: '#323130',
      900: '#201F1E',
    },
  },
  typography: {
    fontFamily: '"Segoe UI", -apple-system, BlinkMacSystemFont, "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.75rem',
      fontWeight: 600,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '2.25rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
  },
  shape: {
    borderRadius: 4,
  },
  shadows: [
    'none',
    '0px 1.6px 3.6px rgba(0, 0, 0, 0.13), 0px 0.3px 0.9px rgba(0, 0, 0, 0.11)',
    '0px 3.2px 7.2px rgba(0, 0, 0, 0.13), 0px 0.6px 1.8px rgba(0, 0, 0, 0.11)',
    '0px 6.4px 14.4px rgba(0, 0, 0, 0.13), 0px 1.2px 3.6px rgba(0, 0, 0, 0.11)',
    '0px 12.8px 28.8px rgba(0, 0, 0, 0.13), 0px 2.4px 7.2px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
    '0px 25.6px 57.6px rgba(0, 0, 0, 0.13), 0px 4.8px 14.4px rgba(0, 0, 0, 0.11)',
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 4,
          padding: '8px 20px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 1.6px 3.6px rgba(0, 0, 0, 0.13), 0px 0.3px 0.9px rgba(0, 0, 0, 0.11)',
          },
        },
        contained: {
          '&:hover': {
            transform: 'translateY(-1px)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0px 1.6px 3.6px rgba(0, 0, 0, 0.13), 0px 0.3px 0.9px rgba(0, 0, 0, 0.11)',
          '&:hover': {
            boxShadow: '0px 3.2px 7.2px rgba(0, 0, 0, 0.13), 0px 0.6px 1.8px rgba(0, 0, 0, 0.11)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 4,
          },
        },
      },
    },
  },
})