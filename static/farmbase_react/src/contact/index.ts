// Export all contact components
export { default as TableInstance } from './TableInstance'
export { default as ContactPopover } from './ContactPopover'
export { default as ContactCreateEditDialog } from './ContactCreateEditDialog'
export { default as ChatDrawer } from './ChatDrawer'
export { default as ContactFilterDialog } from './ContactFilterDialog'

// Export contact store
export { useContactStore } from '../stores/contactStore'
export type { Contact, ContactListOptions, ContactEngagement, ContactFilter, ChatState, ContactInstance } from '../stores/contactStore'