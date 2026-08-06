import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Analytics from './pages/Analytics'
import Comments from './pages/Comments'
import Dashboard from './pages/Dashboard'
import Studio from './pages/Studio'
import UploadManager from './pages/UploadManager'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="studio" element={<Studio />} />
          <Route path="comments" element={<Comments />} />
          <Route path="upload" element={<UploadManager />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
