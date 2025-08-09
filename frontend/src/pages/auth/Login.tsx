import React, { useState } from 'react'
import {
  Box,
  Container,
  Typography,
  TextField,
  Link,
  Alert,
  Paper,
  InputAdornment,
  IconButton,
} from '@mui/material'
import { styled } from '@mui/material/styles'
import {
  Visibility,
  VisibilityOff,
  Email as EmailIcon,
  Lock as LockIcon,
} from '@mui/icons-material'
import { Button } from '../../components/common'
import { useNavigate } from 'react-router-dom'

const LoginContainer = styled(Box)(({ theme }) => ({
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: `linear-gradient(135deg, ${theme.palette.grey[50]} 0%, ${theme.palette.background.default} 100%)`,
  position: 'relative',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'radial-gradient(circle at 50% 50%, rgba(0, 120, 212, 0.08) 0%, transparent 70%)',
    pointerEvents: 'none',
  },
}))

const LoginPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(6),
  borderRadius: 16,
  boxShadow: '0px 10px 40px rgba(0, 0, 0, 0.08)',
  background: theme.palette.background.paper,
  position: 'relative',
  overflow: 'hidden',
  '&::after': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 4,
    background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
  },
}))

const Logo = styled(Typography)(({ theme }) => ({
  fontWeight: 700,
  fontSize: '2rem',
  color: theme.palette.primary.main,
  marginBottom: theme.spacing(1),
  textAlign: 'center',
}))

export const Login: React.FC = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // TODO: Implement actual login logic
      await new Promise(resolve => setTimeout(resolve, 1000))
      navigate('/dashboard')
    } catch (err) {
      setError('Ungültige E-Mail oder Passwort')
    } finally {
      setLoading(false)
    }
  }

  return (
    <LoginContainer>
      <Container maxWidth="sm">
        <LoginPaper elevation={0}>
          <Box sx={{ mb: 4 }}>
            <Logo>VocalIQ</Logo>
            <Typography
              variant="body2"
              color="text.secondary"
              align="center"
            >
              KI-gestützte Telefon-Assistenten
            </Typography>
          </Box>

          <Typography
            variant="h5"
            sx={{ fontWeight: 600, mb: 3, textAlign: 'center' }}
          >
            Willkommen zurück
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="E-Mail"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <EmailIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Passwort"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Box sx={{ mb: 3, textAlign: 'right' }}>
              <Link
                href="#"
                underline="hover"
                sx={{ color: 'primary.main', fontSize: '0.875rem' }}
              >
                Passwort vergessen?
              </Link>
            </Box>

            <Button
              fullWidth
              variant="contained"
              type="submit"
              size="large"
              loading={loading}
              gradient
            >
              Anmelden
            </Button>
          </form>

          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Noch kein Konto?{' '}
              <Link
                href="#"
                underline="hover"
                sx={{ color: 'primary.main', fontWeight: 600 }}
                onClick={(e) => {
                  e.preventDefault()
                  navigate('/register')
                }}
              >
                Jetzt registrieren
              </Link>
            </Typography>
          </Box>
        </LoginPaper>
      </Container>
    </LoginContainer>
  )
}