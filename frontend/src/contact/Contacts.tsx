import React from 'react'
import { ContactStoreProvider } from '@/stores/contactStore'
import { withApiClient, type ApiClient } from '@/api/client'
import TableInstance from './TableInstance'
import ChatDrawer from './ChatDrawer'
import ContactCreateEditDialog from './ContactCreateEditDialog'
import ContactFilterDialog from './ContactFilterDialog'
import MemoriesDrawer from './MemoriesDrawer'

interface ContactsProps {
    apiClient: ApiClient
}

// Inner component that renders all contact-related components
const ContactsContent: React.FC = () => {
    return (
        <React.Fragment>
            <TableInstance />
            <ChatDrawer />
            <ContactCreateEditDialog />
            <ContactFilterDialog />
            <MemoriesDrawer />
        </React.Fragment>
    )
}

// Main component that provides the store
const Contacts: React.FC<ContactsProps> = ({ apiClient }) => {
    return (
        <ContactStoreProvider apiClient={apiClient}>
            <ContactsContent />
        </ContactStoreProvider>
    )
}

export default withApiClient(Contacts)