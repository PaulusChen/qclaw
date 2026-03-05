import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Layout from './index'

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>)
}

describe('Layout', () => {
  it('renders header with logo', () => {
    renderWithRouter(<Layout />)
    expect(screen.getByText(/🤖 QCLaw/i)).toBeInTheDocument()
  })

  it('renders navigation menu', () => {
    renderWithRouter(<Layout />)
    expect(screen.getByText(/大盘指标/i)).toBeInTheDocument()
    expect(screen.getByText(/量化指标/i)).toBeInTheDocument()
    expect(screen.getByText(/新闻资讯/i)).toBeInTheDocument()
  })

  it('renders footer', () => {
    renderWithRouter(<Layout />)
    expect(screen.getByText(/QCLaw 投资分析仪表盘/i)).toBeInTheDocument()
  })
})
