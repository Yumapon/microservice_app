/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import React from 'react'
import { useNavigate } from 'react-router-dom'

const TermsPage: React.FC = () => {
  const navigate = useNavigate()

  return (
    <main style={styles.container}>
      <div css={navBarStyle}>
          <button css={backButtonStyle} onClick={() => navigate('/')}>
          ← TopPageに戻る
          </button>
      </div>
      <h1 style={styles.heading}>利用規約</h1>

      <section style={styles.section}>
        <h2>第1条（適用）</h2>
        <p>
          本利用規約（以下「本規約」といいます。）は、当社（以下「当社」といいます。）が提供する保険関連サービス（以下「本サービス」といいます。）の利用に関する条件を定めるものです。ユーザーは本規約に同意の上、本サービスを利用するものとします。
        </p>
      </section>

      <section style={styles.section}>
        <h2>第2条（利用登録）</h2>
        <p>
          本サービスの利用を希望する者は、当社の定める方法により登録を申請し、当社がこれを承認することで利用登録が完了するものとします。
        </p>
      </section>

      <section style={styles.section}>
        <h2>第3条（禁止事項）</h2>
        <ul>
          <li>法令または公序良俗に違反する行為</li>
          <li>他者の知的財産権を侵害する行為</li>
          <li>当社サービスの運営を妨害する行為</li>
          <li>虚偽の情報を登録・発信する行為</li>
        </ul>
      </section>

      <section style={styles.section}>
        <h2>第4条（サービスの提供の停止等）</h2>
        <p>
          当社は以下のいずれかに該当する場合、ユーザーに事前に通知することなく本サービスの全部または一部の提供を停止または中断することができます。
        </p>
        <ul>
          <li>本サービスにかかるシステムの保守点検または更新を行う場合</li>
          <li>火災、停電、天災等の不可抗力によりサービス提供が困難となった場合</li>
        </ul>
      </section>

      <section style={styles.section}>
        <h2>第5条（著作権）</h2>
        <p>
          本サービスに関する著作権、商標権その他の知的財産権はすべて当社または正当な権利を有する第三者に帰属します。ユーザーは、当該権利を侵害する行為を行ってはなりません。
        </p>
      </section>

      <section style={styles.section}>
        <h2>第6条（免責事項）</h2>
        <p>
          本サービスの利用に関してユーザーに生じた損害について、当社は一切の責任を負わないものとします。
        </p>
      </section>

      <section style={styles.section}>
        <h2>第7条（規約の変更）</h2>
        <p>
          当社は、必要と判断した場合にはユーザーに通知することなく本規約を変更することがあります。
        </p>
      </section>

      <section style={styles.section}>
        <h2>第8条（準拠法および裁判管轄）</h2>
        <p>
          本規約の解釈にあたっては、日本法を準拠法とします。本サービスに関して紛争が生じた場合には、東京地方裁判所を専属的合意管轄裁判所とします。
        </p>
      </section>

      <p>制定日：2025年7月17日</p>
    </main>
  )
}

export default TermsPage

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '2rem',
    fontFamily: 'Helvetica, Arial, sans-serif',
    backgroundColor: '#fdfdfd',
    color: '#333',
    lineHeight: 1.8,
  },
  heading: {
    borderBottom: '2px solid #ccc',
    paddingBottom: '0.5rem',
    marginBottom: '2rem',
  },
  section: {
    marginBottom: '2rem',
  },
}

const navBarStyle = css`
  margin-bottom: 1rem;
`

const backButtonStyle = css`
  background: none;
  border: none;
  color: #0ea5e9;
  font-size: 0.95rem;
  text-decoration: underline;
  cursor: pointer;

  &:hover {
    opacity: 0.8;
  }
`