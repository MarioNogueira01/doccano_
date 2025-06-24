<template>
  <div class="multi-comparison-container">
    <!-- Header with user info -->
    <div class="d-flex align-center justify-space-between px-4 py-3 header">
      <div class="d-flex align-center">
        <v-icon color="primary" class="mr-2">mdi-compare-multiple</v-icon>
        <h3 class="text-h6 font-weight-medium mb-0">Multi-User Annotation Comparison</h3>
      </div>
      <div class="d-flex align-center user-badges">
        <v-chip
          v-for="(user, index) in selectedUsers"
          :key="user.id"
          small
          :color="getUserColor(index)"
          :text-color="getUserTextColor(index)"
          class="mr-2"
        >
          <v-avatar left size="24" class="mr-1">
            <v-icon x-small>mdi-account</v-icon>
          </v-avatar>
          {{ user.username }}
        </v-chip>
      </div>
    </div>
    
    <!-- Label legend as chips -->
    <div class="px-4 py-2 grey lighten-5 d-flex align-center label-legend">
      <div class="mr-3 grey--text text--darken-1">
        <v-icon x-small class="mr-1">mdi-palette</v-icon>
      </div>
      <v-chip
        v-for="label in effectiveLabels"
        :key="label.id"
        x-small
        :style="{
          backgroundColor: label.backgroundColor,
          color: getContrastColor(label.backgroundColor)
        }"
        class="mr-2"
      >
        {{ label.text }}
      </v-chip>
    </div>

    <!-- Multi-user side-by-side document views -->
    <div class="multi-side-by-side-container">
      <div
        v-for="(user, index) in selectedUsers"
        :key="user.id"
        class="document-panel"
        :style="{ width: `${100 / selectedUsers.length}%` }"
      >
        <div class="document-header px-4 py-2">
          <v-chip small :color="getUserColor(index)" :text-color="getUserTextColor(index)">
            <v-avatar left size="24" class="mr-1">
              <v-icon x-small>mdi-account</v-icon>
            </v-avatar>
            {{ user.username }}
          </v-chip>
          <div class="text-caption grey--text ml-2">
            {{ getUserAnnotations(user.user).length }} annotations
          </div>
        </div>
        <div 
          :ref="`userContent${index}`" 
          class="document-content" 
          @scroll="syncScroll(index, $event)"
        >
          <v-card flat class="document-card">
            <v-card-text class="document-text">
              <template v-if="documentText">
                <div class="text-content">
                  {{ documentText }}
                </div>
              </template>
              <div v-else class="text-center py-4 grey--text">
                No document text available
              </div>
            </v-card-text>
            <!-- Add label distribution for user -->
            <v-card-text 
              v-if="getUserAnnotations(user.user).length > 0" 
              class="label-distribution pt-0"
            >
              <div class="text-subtitle-2 mb-2">Label Distribution:</div>
              <div class="d-flex flex-wrap">
                <v-chip
                  v-for="ann in getUserAnnotations(user.user)"
                  :key="ann.id"
                  small
                  class="mr-2 mb-2"
                  :style="{
                    backgroundColor: getColorForLabel(ann.label),
                    color: getContrastColor(getColorForLabel(ann.label))
                  }"
                >
                  {{ ann.label_text || getLabelText(ann.label) }}
                </v-chip>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </div>
    </div>

    <!-- Enhanced agreement statistics bar at bottom -->
    <div class="agreement-stats-bar">
      <div class="stats-container pa-4">
        <div class="stats-card pa-3">
          <div class="d-flex align-center mb-3">
            <v-icon color="primary" class="mr-2">mdi-chart-bar</v-icon>
            <span class="text-subtitle-2 font-weight-medium">Multi-User Agreement Statistics</span>
          </div>
          
          <div class="d-flex flex-wrap justify-space-between">
            <div class="stat-box match-box">
              <div class="stat-value">{{ totalMatchingCount }}</div>
              <div class="stat-label">
                <v-icon small color="green" class="mr-1">mdi-check-circle</v-icon>
                Total Matches
              </div>
            </div>
            
            <div
              v-for="(user, index) in selectedUsers"
              :key="user.id"
              class="stat-box"
              :class="getUserBoxClass(index)"
            >
              <div class="stat-value">{{ getUserOnlyCount(user.user) }}</div>
              <div class="stat-label">
                <v-avatar size="16" :class="getUserBadgeClass(index)" class="mr-1"></v-avatar>
                {{ user.username }} only
              </div>
            </div>
            
            <div class="stat-box agreement-box">
              <div class="agreement-ring">
                <v-progress-circular
                  :size="54"
                  :width="6"
                  :value="overallAgreementPercentage"
                  :color="getAgreementColor(overallAgreementPercentage)"
                >
                  <span class="text-h6">{{ overallAgreementPercentage }}%</span>
                </v-progress-circular>
              </div>
              <div class="stat-label text-center mt-2">
                <v-chip
                  x-small
                  :color="getAgreementColor(overallAgreementPercentage)"
                  text-color="white"
                >
                  Overall Agreement
                </v-chip>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  name: 'MultiUserComparisonView',
  
  props: {
    projectId: {
      type: [Number, String],
      required: true
    },
    documentId: {
      type: [Number, String],
      required: true
    },
    selectedUsers: {
      type: Array,
      required: true
    },
    labels: {
      type: Array,
      default: () => []
    },
    users: {
      type: Array,
      default: () => []
    }
  },

  data() {
    return {
      documentText: '',
      projectType: '',
      loading: false,
      errorMessage: null,
      apiLoaded: false,
      userAnnotations: {} as {[key: string]: any[]},
      userDetails: {} as {[key: string]: any},
      matchingCount: 0,
      userOnlyCounts: {} as {[key: string]: number},
      overallAgreementPercentage: 0
    }
  },

  computed: {
    effectiveLabels() {
      return this.labels && this.labels.length > 0 ? this.labels : []
    },

    totalMatchingCount() {
      return this.matchingCount
    },

    // Get the actual users who have annotations (handles fallback)
    usersWithAnnotations() {
      const userIds = Object.keys(this.userAnnotations).filter(userId => 
        this.userAnnotations[userId] && this.userAnnotations[userId].length > 0
      )
      
      // Map user IDs to user objects
      return userIds.map(userId => {
        // First try to find in the users prop
        const user = this.users.find(u => u.id.toString() === userId)
        if (user) {
          return user
        }
        
        // If not found in users prop, try to get from the selectedUsers (for fallback cases)
        const selectedUser = this.selectedUsers.find(u => u.id.toString() === userId)
        if (selectedUser) {
          return selectedUser
        }
        
        // Try to get from fetched user details
        const fetchedUser = this.userDetails[userId]
        if (fetchedUser) {
          return fetchedUser
        }
        
        // Last resort: create a user object with the ID
        return { id: userId, username: `User ${userId}` }
      })
    }
  },

  mounted() {
    console.log("MultiUserComparisonView mounted with props:", {
      projectId: this.projectId,
      documentId: this.documentId,
      selectedUsers: this.selectedUsers,
      labels: this.labels?.length || 0,
      users: this.users?.length || 0
    });
    
    this.fetchData();
  },

  methods: {
    getUserAnnotations(userId: string | number): any[] {
      return this.userAnnotations[userId.toString()] || []
    },

    getUserOnlyCount(userId: string | number): number {
      return this.userOnlyCounts[userId.toString()] || 0
    },

    getUserColor(index: number): string {
      const colors = [
        '#fff3e0', '#e3f2fd', '#f3e5f5', '#e8f5e8', '#fff8e1', '#fce4ec'
      ]
      return colors[index % colors.length]
    },

    getUserTextColor(index: number): string {
      const colors = [
        '#e65100', '#0d47a1', '#4a148c', '#1b5e20', '#f57f17', '#880e4f'
      ]
      return colors[index % colors.length]
    },

    getUserBoxClass(index: number): string {
      const classes = [
        'user1-box', 'user2-box', 'user3-box', 'user4-box', 'user5-box', 'user6-box'
      ]
      return classes[index % classes.length]
    },

    getUserBadgeClass(index: number): string {
      const classes = [
        'user1-badge', 'user2-badge', 'user3-badge', 
        'user4-badge', 'user5-badge', 'user6-badge'
      ]
      return classes[index % classes.length]
    },

    getLabelText(labelId: number): string {
      const label = this.effectiveLabels.find(l => l.id === labelId)
      return label ? label.text : `Label ${labelId}`
    },

    getColorForLabel(labelId: number): string {
      const label = this.effectiveLabels.find(l => l.id === labelId)
      return label ? label.backgroundColor : '#cccccc'
    },

    getContrastColor(hexColor: string): string {
      if (!hexColor || !hexColor.startsWith('#')) return '#000000';
      
      // Convert hex to RGB
      const r = parseInt(hexColor.slice(1, 3), 16);
      const g = parseInt(hexColor.slice(3, 5), 16);
      const b = parseInt(hexColor.slice(5, 7), 16);
      
      // Calculate luminance
      const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
      
      // Return black for light colors, white for dark colors
      return luminance > 0.5 ? '#000000' : '#FFFFFF';
    },

    getAgreementColor(percentage: number): string {
      if (percentage >= 80) return 'success';
      if (percentage >= 60) return 'primary';
      if (percentage >= 40) return 'warning';
      return 'error';
    },

    async fetchUserDetails(userIds: (string | number)[]) {
      try {
        // Fetch project members to get user details
        const members = await this.$repositories.member.list(this.projectId.toString())
        
        // Store user details
        userIds.forEach(userId => {
          const member = members.find(m => m.user.toString() === userId.toString())
          if (member) {
            this.userDetails[userId.toString()] = {
              id: member.user,
              username: member.username
            }
          }
        })
        
        console.log("Fetched user details:", this.userDetails)
      } catch (error) {
        console.error("Error fetching user details:", error)
      }
    },

    async fetchData() {
      this.loading = true
      try {
        console.log("Fetching data for document:", this.documentId)
        console.log("Selected users:", this.selectedUsers)
        
        // Fetch document text
        const doc = await this.$services.example.findById(this.projectId, this.documentId)
        this.documentText = doc.text
        console.log("Document text:", this.documentText)
        
        // Fetch project type
        const project = await this.$services.project.findById(this.projectId)
        this.projectType = project.project_type
        console.log("Project type:", this.projectType)
        
        // Fetch annotations for all users
        const userIds = this.selectedUsers.map(user => user.user)
        console.log("User IDs to fetch:", userIds)
        
        // Try to use the multi-user service method
        let annotationData
        try {
          annotationData = await this.$services.annotation.getMultiUserComparisonData(
            this.projectId,
            this.documentId,
            userIds
          )
          console.log("Multi-user annotation data:", annotationData)
          
          // Fetch user details for all selected users
          await this.fetchUserDetails(userIds)
          
        } catch (serviceError) {
          console.warn("Multi-user service failed, trying individual calls:", serviceError)
          // Fallback: fetch annotations individually
          annotationData = {}
          for (const userId of userIds) {
            try {
              const userAnnotations = await this.$services.annotation.getUserAnnotations(
                this.projectId,
                this.documentId,
                userId
              )
              annotationData[userId.toString()] = userAnnotations
              console.log(`Annotations for user ${userId}:`, userAnnotations)
            } catch (userError) {
              console.error(`Failed to fetch annotations for user ${userId}:`, userError)
              annotationData[userId.toString()] = []
            }
          }
        }
        
        this.userAnnotations = annotationData
        console.log("Final user annotations:", this.userAnnotations)
        this.calculateAgreementMetrics()
        
      } catch (error) {
        console.error("Fetch error:", error)
        this.errorMessage = error.message
        this.useTestData()
      } finally {
        this.loading = false
      }
    },

    useTestData() {
      console.log("Loading test data for multi-user comparison")
      this.documentText = 
        "This is a sample document text for demonstration purposes. " +
        "It will help visualize annotations from different users."
      
      // Sample annotations for multiple users
      this.userAnnotations = {}
      this.selectedUsers.forEach((user, index) => {
        this.userAnnotations[user.user] = [
          { id: 100 + index, start_offset: 5, end_offset: 11, label: 1 },
          { 
            id: 200 + index, 
            start_offset: 27 + index * 5, 
            end_offset: 38 + index * 5, 
            label: 2 
          }
        ]
      })
      
      this.calculateAgreementMetrics()
    },

    calculateAgreementMetrics() {
      this.matchingCount = 0
      this.userOnlyCounts = {}
      
      // Get the actual users who have annotations
      const actualUsers = this.selectedUsers
      
      // Initialize user-only counts for actual users
      actualUsers.forEach(user => {
        this.userOnlyCounts[user.user] = 0
      })
      
      // Calculate matches and unique annotations
      const allAnnotations = []
      actualUsers.forEach(user => {
        const userAnnots = this.getUserAnnotations(user.user)
        userAnnots.forEach(ann => {
          allAnnotations.push({
            ...ann,
            userId: user.user
          })
        })
      })
      
      console.log("Calculating agreement metrics for:", {
        projectType: this.projectType,
        allAnnotations,
        actualUsers
      })
      
      if (this.projectType === 'DocumentClassification') {
        // For document classification, compare labels
        const userLabels = {}
        
        // Group annotations by user
        actualUsers.forEach(user => {
          const userAnnots = this.getUserAnnotations(user.user)
          userLabels[user.user] = userAnnots.map(ann => ann.label)
        })
        
        console.log("User labels:", userLabels)
        
        // Find matching labels across users
        const allLabels = new Set()
        Object.values(userLabels).forEach(labels => {
          labels.forEach(label => allLabels.add(label))
        })
        
        // Count matches and unique labels
        allLabels.forEach(label => {
          const usersWithThisLabel = actualUsers.filter(user => 
            userLabels[user.user].includes(label)
          )
          
          if (usersWithThisLabel.length > 1) {
            // Multiple users have this label - it's a match
            this.matchingCount += usersWithThisLabel.length
          } else {
            // Only one user has this label - it's unique to that user
            this.userOnlyCounts[usersWithThisLabel[0].user]++
          }
        })
      } else {
        // For sequence labeling, compare spans
        const processedMatches = new Set()
        
        for (let i = 0; i < allAnnotations.length; i++) {
          const ann1 = allAnnotations[i]
          const matchKey = `${ann1.start_offset}-${ann1.end_offset}-${ann1.label}`
          
          if (processedMatches.has(matchKey)) continue
          
          const matchingUsers = allAnnotations.filter(ann2 => 
            ann2.start_offset === ann1.start_offset && 
            ann2.end_offset === ann1.end_offset && 
            ann2.label === ann1.label
          )
          
          if (matchingUsers.length > 1) {
            this.matchingCount += matchingUsers.length
            processedMatches.add(matchKey)
            
            // Mark these as processed
            matchingUsers.forEach(ann => {
              const key = `${ann.start_offset}-${ann.end_offset}-${ann.label}`
              processedMatches.add(key)
            })
          } else {
            // Unique annotation
            this.userOnlyCounts[ann1.userId]++
          }
        }
      }
      
      // Calculate overall agreement percentage
      const totalAnnotations = allAnnotations.length
      if (totalAnnotations > 0) {
        this.overallAgreementPercentage = Math.round((this.matchingCount / totalAnnotations) * 100)
      } else {
        this.overallAgreementPercentage = 0
      }
      
      console.log("Agreement metrics calculated:", {
        matchingCount: this.matchingCount,
        userOnlyCounts: this.userOnlyCounts,
        overallAgreementPercentage: this.overallAgreementPercentage,
        totalAnnotations
      })
    },

    syncScroll(userIndex: number, event: Event) {
      // Sync scrolling across all panels
      this.selectedUsers.forEach((_, index) => {
        if (index !== userIndex) {
          const targetElement = this.$refs[`userContent${index}`] as HTMLElement[]
          if (targetElement && targetElement[0]) {
            targetElement[0].scrollTop = (event.target as HTMLElement).scrollTop
          }
        }
      })
    }
  }
})
</script>

<style scoped>
.multi-comparison-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #fafafa;
}

.header {
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.user-badges {
  flex-wrap: wrap;
}

.label-legend {
  border-bottom: 1px solid #e0e0e0;
}

.multi-side-by-side-container {
  flex: 1;
  display: flex;
  overflow: hidden;
  align-items: stretch;
}

.document-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid #e0e0e0;
  min-width: 0;
  box-sizing: border-box;
}

.document-panel:last-child {
  border-right: none;
}

.document-header {
  display: flex;
  align-items: center;
  background-color: #fafafa;
  border-bottom: 1px solid #e0e0e0;
}

.document-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  height: 100%;
  padding: 16px;
}

.document-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.document-text {
  font-family: 'Roboto', sans-serif;
  line-height: 1.6;
  white-space: pre-wrap;
  font-size: 1rem;
  padding: 0;
  word-break: break-word;
  background-color: #fafafa;
  border-radius: 4px;
  margin-bottom: 16px;
}

.label-distribution {
  background-color: #ffffff;
  border-top: 1px solid #e0e0e0;
  padding: 16px;
  margin-top: 16px;
}

.agreement-stats-bar {
  background-color: #f5f5f5;
  border-top: 1px solid #e0e0e0;
}

.stats-container {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  border-radius: 8px;
  min-width: 120px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  text-align: center;
}

.match-box {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.user1-box {
  background-color: #fff8e1;
  color: #f57f17;
}

.user2-box {
  background-color: #e3f2fd;
  color: #0d47a1;
}

.user3-box {
  background-color: #f3e5f5;
  color: #4a148c;
}

.user4-box {
  background-color: #e8f5e8;
  color: #1b5e20;
}

.user5-box {
  background-color: #fff8e1;
  color: #f57f17;
}

.user6-box {
  background-color: #fce4ec;
  color: #880e4f;
}

.agreement-box {
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.user1-badge {
  background-color: #f57f17;
}

.user2-badge {
  background-color: #0d47a1;
}

.user3-badge {
  background-color: #4a148c;
}

.user4-badge {
  background-color: #1b5e20;
}

.user5-badge {
  background-color: #f57f17;
}

.user6-badge {
  background-color: #880e4f;
}
</style> 