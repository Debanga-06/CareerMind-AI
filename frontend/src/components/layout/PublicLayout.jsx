import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-paper">
      <Navbar />
      <Outlet />
      <footer className="border-t border-line py-8">
        <div className="container-page flex flex-col items-center justify-between gap-3 text-sm text-muted sm:flex-row">
          <p>© {new Date().getFullYear()} CareerGraph AI</p>
          <p>Job data via SerpApi · Analysis runs on your own backend</p>
        </div>
      </footer>
    </div>
  )
}
