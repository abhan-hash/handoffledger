import React from 'react'
import { SuccessorView, SuccessorViewProps } from './SuccessorView'

export type { SuccessorViewProps }

export const SuccessorRunway: React.FC<SuccessorViewProps> = (props) => {
  return <SuccessorView {...props} />
}

export default SuccessorRunway
