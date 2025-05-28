<template>
  <v-navigation-drawer
    v-model="isOpen"
    location="right"
    temporary
    width="800"
    class="chat-drawer"
  >
    <v-card flat>
      <v-card-title class="d-flex align-center justify-space-between">
        <span>Chat History</span>
        <v-btn icon variant="text" @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      
      <v-divider />
      
      <v-card-text v-if="loading" class="text-center">
        <v-progress-circular indeterminate />
        <div class="mt-2">Loading chat history...</div>
      </v-card-text>
      
      <v-card-text v-else-if="error" class="text-center">
        <v-alert type="error" variant="tonal">
          {{ error }}
        </v-alert>
      </v-card-text>
      
      <v-card-text v-else class="chat-content">
        <div v-if="chatState?.last_agent" class="mb-4">
          <v-chip color="primary" variant="tonal">
            Last Agent: {{ chatState.last_agent.name }}
          </v-chip>
        </div>
        
        <div v-if="chatState?.input_list?.length === 0" class="text-center text-grey">
          No chat history available
        </div>
        
        <div v-else class="chat-messages">
          <div
            v-for="(item, index) in filteredInputList"
            :key="index"
            class="message-item mb-3"
          >
            <v-card variant="outlined" :class="getMessageClass(item.role)">
              <v-card-subtitle class="pb-1">
                <v-chip size="small" :color="getRoleColor(item.role)">
                  {{ item.role }}
                </v-chip>
              </v-card-subtitle>
              
              <v-card-text class="pt-0">
                <div v-if="item.content && Array.isArray(item.content)">
                  <div
                    v-for="(content, contentIndex) in item.content"
                    :key="contentIndex"
                    class="content-item mb-2"
                  >
                    <div v-if="content.type === 'input_text' || content.type === 'output_text'">
                      <pre class="text-wrap">{{ content.text }}</pre>
                    </div>
                    <div v-else-if="content.type === 'input_image'">
                      <v-chip size="small" color="info">
                        📷 Image uploaded
                      </v-chip>
                      <div v-if="content.detail" class="text-caption text-grey mt-1">
                        Detail: {{ content.detail }}
                      </div>
                      <div v-if="content.file_id" class="text-caption text-grey">
                        File ID: {{ content.file_id }}
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else-if="typeof item.content === 'string'">
                  <pre class="text-wrap">{{ item.content }}</pre>
                </div>
                <div v-else-if="item.content">
                  <pre class="text-wrap">{{ JSON.stringify(item.content, null, 2) }}</pre>
                </div>
              </v-card-text>
            </v-card>
          </div>
        </div>
      </v-card-text>
    </v-card>
  </v-navigation-drawer>
</template>

<script>
import api from "@/api"

export default {
  name: "ChatDrawer",
  
  props: {
    contactId: {
      type: Number,
      default: null,
    },
  },
  
  data() {
    return {
      isOpen: false,
      loading: false,
      error: null,
      chatState: null,
    }
  },
  
  computed: {
    filteredInputList() {
      if (!this.chatState?.input_list) return []
      
      // Filter out function_call and function_call_output items
      return this.chatState.input_list.filter(item => 
        item.type !== 'function_call' && item.type !== 'function_call_output'
      )
    },
  },
  
  methods: {
    async open(contactId) {
      this.isOpen = true
      if (contactId) {
        await this.loadChatState(contactId)
      }
    },
    
    close() {
      this.isOpen = false
      this.chatState = null
      this.error = null
    },
    
    async loadChatState(contactId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.get(`/chatstate?contact_id=${contactId}`)
        this.chatState = response.data
      } catch (error) {
        console.error('Error loading chat state:', error)
        this.error = 'Failed to load chat history'
      } finally {
        this.loading = false
      }
    },
    
    getRoleColor(role) {
      switch (role) {
        case 'user':
          return 'blue'
        case 'assistant':
          return 'green'
        case 'system':
          return 'orange'
        default:
          return 'grey'
      }
    },
    
    getMessageClass(role) {
      return {
        'user-message': role === 'user',
        'assistant-message': role === 'assistant',
        'system-message': role === 'system',
      }
    },
  },
}
</script>

<style scoped>
.chat-drawer {
  z-index: 1000;
}

.chat-content {
  max-height: 70vh;
  overflow-y: auto;
}

.message-item {
  margin-bottom: 8px;
}

.user-message {
  margin-left: 20px;
}

.assistant-message {
  margin-right: 20px;
}

.content-item:last-child {
  margin-bottom: 0;
}

.chat-messages {
  padding-bottom: 20px;
}

.text-wrap {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  margin: 0;
  background: none;
  font-size: 0.875rem;
}
</style>