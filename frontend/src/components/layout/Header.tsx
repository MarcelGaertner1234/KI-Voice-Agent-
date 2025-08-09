import React, { useState } from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Container,
  Menu,
  MenuItem,
  Avatar,
  Divider,
} from '@mui/material'
import { styled } from '@mui/material/styles'
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material'
import { Button } from '../common/Button'
import { useNavigate } from 'react-router-dom'

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  color: theme.palette.text.primary,
  boxShadow: '0px 1px 0px rgba(0, 0, 0, 0.08)',
  borderBottom: `1px solid ${theme.palette.grey[200]}`,
}))

const Logo = styled(Typography)(({ theme }) => ({
  fontWeight: 600,
  fontSize: '1.25rem',
  color: theme.palette.primary.main,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
}))

const NavLink = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.secondary,
  cursor: 'pointer',
  fontWeight: 500,
  transition: 'color 0.2s',
  '&:hover': {
    color: theme.palette.primary.main,
  },
}))

export const Header: React.FC = () => {
  const navigate = useNavigate()
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleUserMenuClose = () => {
    setAnchorEl(null)
  }

  const handleLogout = () => {
    // TODO: Implement logout logic
    navigate('/login')
  }

  return (
    <StyledAppBar position="fixed" elevation={0}>
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <Logo onClick={() => navigate('/')}>
            VocalIQ
          </Logo>

          {/* Desktop Navigation */}
          <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' }, ml: 4, gap: 3 }}>
            <NavLink onClick={() => navigate('/dashboard')}>Dashboard</NavLink>
            <NavLink onClick={() => navigate('/agents')}>Agents</NavLink>
            <NavLink onClick={() => navigate('/calls')}>Anrufe</NavLink>
            <NavLink onClick={() => navigate('/customers')}>Kunden</NavLink>
            <NavLink onClick={() => navigate('/analytics')}>Analysen</NavLink>
          </Box>

          {/* User Menu */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              variant="outlined"
              size="small"
              sx={{ display: { xs: 'none', sm: 'inline-flex' } }}
              onClick={() => navigate('/new-agent')}
            >
              Neuer Agent
            </Button>
            
            <IconButton onClick={handleUserMenuOpen}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                <PersonIcon fontSize="small" />
              </Avatar>
            </IconButton>

            {/* Mobile Menu Button */}
            <IconButton
              sx={{ display: { xs: 'flex', md: 'none' } }}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <CloseIcon /> : <MenuIcon />}
            </IconButton>
          </Box>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleUserMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            PaperProps={{
              sx: {
                mt: 1.5,
                minWidth: 200,
              },
            }}
          >
            <MenuItem onClick={() => navigate('/profile')}>
              <PersonIcon fontSize="small" sx={{ mr: 1.5 }} />
              Profil
            </MenuItem>
            <MenuItem onClick={() => navigate('/settings')}>
              <SettingsIcon fontSize="small" sx={{ mr: 1.5 }} />
              Einstellungen
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <LogoutIcon fontSize="small" sx={{ mr: 1.5 }} />
              Abmelden
            </MenuItem>
          </Menu>
        </Toolbar>
      </Container>
    </StyledAppBar>
  )
}