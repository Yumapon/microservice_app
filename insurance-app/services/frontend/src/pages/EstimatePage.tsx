/** @jsxImportSource @emotion/react */
import { useState } from 'react'
import { PensionEstimateForm } from '@/components/EstimatePage/PensionEstimateForm'
import EducationEstimateForm from '@/components/EstimatePage/EducationEstimateForm'
import { ProductSelectGrid } from '@/components/EstimatePage/ProductSelectGrid'
import { UnderConstructionForm } from '@/components/EstimatePage/UnderConstructionForm'
import { useNavigate } from 'react-router-dom'

import MyPageLayout from '@/components/layout/MyPageLayout'

const EstimatePage = () => {
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null)
  const navigate = useNavigate() 

  const renderForm = () => {
    switch (selectedProduct) {
      case 'pension':
        return <PensionEstimateForm />
      case 'education':
        return <EducationEstimateForm />
      case 'work':
      case 'cancer':
      case 'medical':
        return <UnderConstructionForm />
      default:
        return null
    }
  }


  return (
    <MyPageLayout>
      <h1>保険見積もり</h1>
      <ProductSelectGrid selectedId={selectedProduct} onSelect={setSelectedProduct} />

      {renderForm()}

      <div style={{ marginTop: '2rem', textAlign: 'center' }}>
        <button
          onClick={() => navigate('/mypage')}
          style={{
            padding: '0.75rem 2rem',
            backgroundColor: '#e5e7eb',
            border: 'none',
            borderRadius: '9999px',
            fontWeight: 'bold',
            cursor: 'pointer',
            color: '#1f2937',
          }}
        >
          マイページに戻る
        </button>
      </div>
    </MyPageLayout>
  )
}

export default EstimatePage