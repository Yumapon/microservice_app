/** @jsxImportSource @emotion/react */
import styled from '@emotion/styled'
import { css } from '@emotion/react'

const Section = styled.section`
  background: linear-gradient(135deg, #f9f9f9, #e0f7f4);
  padding: 3rem 1.5rem;
`

const Container = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  justify-content: center;
  align-items: center;
  gap: 2rem;

  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
  }
`

const Image = styled.img`
  width: 200px;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);

  @media (max-width: 768px) {
    width: 150px;
  }
`

const Content = styled.div`
  max-width: 400px;

  @media (max-width: 768px) {
    max-width: 100%;
  }
`

const Title = styled.h2`
  font-size: 1.8rem;
  margin-bottom: 0.5rem;

  @media (max-width: 768px) {
    font-size: 1.5rem;
  }
`

const Description = styled.p`
  font-size: 1rem;
  color: #555;
  margin-bottom: 1.2rem;
`

const StepList = styled.ul`
  list-style: none;
  padding: 0;
  margin-bottom: 1.5rem;

  li {
    display: flex;
    align-items: center;
    margin-bottom: 0.8rem;
    font-size: 1rem;

    span {
      background: #1abc9c;
      color: white;
      font-weight: bold;
      width: 28px;
      height: 28px;
      text-align: center;
      line-height: 28px;
      border-radius: 50%;
      margin-right: 0.8rem;
      flex-shrink: 0;
    }

    @media (max-width: 768px) {
      justify-content: center;
    }
  }
`

const Button = styled.button`
  background-color: #1abc9c;
  color: white;
  font-size: 1rem;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);

  &:hover {
    background-color: #16a085;
    transform: translateY(-2px);
  }
`

const sectionStyle = css`
  scroll-margin-top: 80px;
  padding: 2rem 1rem;
`

export const DiagnosisSection = () => {
  return (
    <section id="diagnosis" css={sectionStyle}>
      <Section>
        <Container>
          <Image src="/images/診断.png" alt="診断イメージ" />
          <Content>
            <Title>あなたにぴったりの保険診断</Title>
            <Description>簡単な3問に答えるだけで、最適な保険をご提案！</Description>
            <StepList>
              <li><span>①</span> 年齢・性別を選択</li>
              <li><span>②</span> 家族構成・職業</li>
              <li><span>③</span> 健康状態・希望条件</li>
            </StepList>
            <Button>▶ 診断を始める</Button>
          </Content>
        </Container>
      </Section>
    </section>
  )
}