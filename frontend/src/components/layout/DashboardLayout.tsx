import React from 'react'
import { Outlet } from 'react-router-dom'
import { Box } from '@mui/material'
import { Header } from './Header'

export const DashboardLayout: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Box component="main" sx={{ flex: 1, bgcolor: 'background.default', pt: 8 }}>
        <Outlet />
      </Box>
    </Box>
  )
}