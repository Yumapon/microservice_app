/** @jsxImportSource @emotion/react */
import { css } from '@emotion/react'
import React from 'react'
import { useNavigate } from 'react-router-dom'

const PrivacyPolicyPage: React.FC = () => {
    const navigate = useNavigate()

    return (
        <main style={styles.container}>
        <div css={navBarStyle}>
            <button css={backButtonStyle} onClick={() => navigate('/')}>
            ← TopPageに戻る
            </button>
        </div>
        <h1 style={styles.heading}>プライバシーポリシー</h1>

        <section style={styles.section}>
            <h2>第1条（個人情報の定義）</h2>
            <p>
            「個人情報」とは、氏名、生年月日、住所、電話番号、メールアドレス、その他特定の個人を識別できる情報を指します。
            </p>
        </section>

        <section style={styles.section}>
            <h2>第2条（個人情報の収集方法）</h2>
            <p>
            当社は、ユーザーが利用登録をする際やサービス利用中に、氏名、住所、電話番号、メールアドレス等の情報を収集することがあります。
            </p>
        </section>

        <section style={styles.section}>
            <h2>第3条（個人情報の利用目的）</h2>
            <p>当社が個人情報を収集・利用する目的は以下の通りです：</p>
            <ul>
            <li>本サービスの提供・運営のため</li>
            <li>本人確認のため</li>
            <li>ご利用料金の請求のため</li>
            <li>サービスに関するご案内・お問い合わせ対応のため</li>
            <li>不正利用の防止やセキュリティ対策のため</li>
            </ul>
        </section>

        <section style={styles.section}>
            <h2>第4条（第三者提供の制限）</h2>
            <p>
            当社は、以下の場合を除き、ユーザーの同意なく第三者に個人情報を提供することはありません：
            </p>
            <ul>
            <li>法令に基づく場合</li>
            <li>人の生命、身体または財産の保護のために必要がある場合</li>
            <li>公衆衛生の向上または児童の健全な育成の推進のために特に必要な場合</li>
            </ul>
        </section>

        <section style={styles.section}>
            <h2>第5条（個人情報の開示・訂正・削除）</h2>
            <p>
            ユーザーは、当社に対して自己の個人情報の開示、訂正、削除を求めることができます。適切な本人確認を行った上で、法令に従い対応いたします。
            </p>
        </section>

        <section style={styles.section}>
            <h2>第6条（プライバシーポリシーの変更）</h2>
            <p>
            当社は、本ポリシーの内容を予告なく変更することがあります。変更後の内容は、本ページに掲載された時点で効力を生じます。
            </p>
        </section>

        <section style={styles.section}>
            <h2>第7条（お問い合わせ窓口）</h2>
            <p>
            本ポリシーに関するお問い合わせは、以下の窓口までお願いいたします。
            </p>
            <p>【お問い合わせ窓口】<br />株式会社ダミー<br />Email: contact@example.com</p>
        </section>

        <p>制定日：2025年7月17日</p>
        </main>
    )
}

export default PrivacyPolicyPage

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