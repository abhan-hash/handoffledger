import React from 'react'
import { GapInterview, GapInterviewProps, InterviewQuestion } from './GapInterview'

export type { InterviewQuestion }

export const ExitInterview: React.FC<GapInterviewProps> = (props) => {
  return <GapInterview {...props} />
}

export default ExitInterview
