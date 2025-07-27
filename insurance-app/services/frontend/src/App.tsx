import { ThemeProvider, Global } from '@emotion/react'
import { Provider } from 'react-redux'
import { store } from './store'

import { Theme } from './styles/theme'
import { globalStyle } from './styles/global'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

// ページコンポーネント
import TopPage from './pages/TopPage'
import MyPage from './pages/MyPage'
import NotificationsPage from './pages/NotificationsPage'
import AccountPage from './pages/AccountPage'
import TermsPage from './pages/TermsPage'
import PrivacyPolicyPage from './pages/PrivacyPolicyPage'
import PensionPage from './pages/PensionPage'
import EducationPage from './pages/EducationPage'
import { UnderConstructionPage } from './pages/UnderConstructionPage'
import ContactPage from './pages/ContactPage'
import ContractDetailPage from './pages/ContractDetailPage'
import EstimatePage from './pages/EstimatePage'

function App() {
  return (
    <Provider store={store}>
    <ThemeProvider theme={Theme}>
      <Global styles={globalStyle} />
      <Router>
        <Routes>
          <Route path="/" element={<TopPage />} />
          <Route path="/top" element={<TopPage />} />
          <Route path="/detail/pension" element={<PensionPage />} />
          <Route path="/detail/education" element={<EducationPage />} />
          <Route path="/detail/disability" element={<UnderConstructionPage />} />
          <Route path="/detail/cancer" element={<UnderConstructionPage />} />
          <Route path="/detail/medical" element={<UnderConstructionPage />} />
          <Route path="/mypage" element={<MyPage />} />
          <Route path="/mypage/contracts/:contractId" element={<ContractDetailPage />} />
          <Route path="/mypage/notifications" element={<NotificationsPage />} />
          <Route path="/mypage/profile" element={<AccountPage />} />
          <Route path="mypage/estimate" element={<EstimatePage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
          <Route path="/under-construction" element={<UnderConstructionPage />} />
          <Route path="/contact" element={<ContactPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
    </Provider>
  )
}

export default App