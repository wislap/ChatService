export interface CustomButton {
  id: string
  label: string
  onClick: (messageId: string) => void
  class?: string
}

export interface MessageData {
  id: string
  sender: string
  content: string
  timestamp: number | Date
  type: 'markdown' | 'text' | 'image' | string
  alt?: string
}

export interface ExtendedMessageData extends MessageData {
  editable?: boolean
  showButtons?: boolean
  customButtons?: CustomButton[]
}
