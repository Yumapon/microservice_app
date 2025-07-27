/** @jsxImportSource @emotion/react */
import { css, keyframes } from '@emotion/react'

type SkeletonProps = {
  width?: string
  height?: string
  borderRadius?: string
  style?: React.CSSProperties
  className?: string
}

export const Skeleton = ({
  width = '100%',
  height = '1rem',
  borderRadius = '8px',
  style,
  className,
}: SkeletonProps) => {
  return (
    <div
      css={[skeletonStyle, { width, height, borderRadius }]}
      style={style}
      className={className}
    />
  )
}

const shimmer = keyframes`
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
`

const skeletonStyle = css`
  background: linear-gradient(90deg, #f3f3f3 25%, #e0e0e0 37%, #f3f3f3 63%);
  background-size: 400% 100%;
  animation: ${shimmer} 1.4s ease infinite;
`