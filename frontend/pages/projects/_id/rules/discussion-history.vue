<template>
  <v-card class="pa-4">
    <v-card-title class="d-flex align-center">
      Histórico de Discussões
      <v-spacer />
      <v-select
        v-model="selectedVersionId"
        :items="versionOptions"
        label="Versão"
        outlined
        dense
        style="max-width: 200px"
      />
      <v-btn color="secondary" class="ml-2" @click="$router.back()">Voltar</v-btn>
    </v-card-title>

    <ProjectChat
      :project-id="$route.params.id"
      :version-id="selectedVersionId"
      :read-only="true"
      :key="`chat-${selectedVersionId}`"
    />
  </v-card>
</template>

<script>
import ProjectChat from '~/components/ProjectChat.vue'
export default {
  components: { ProjectChat },
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  data() {
    return {
      versions: [],
      selectedVersionId: null
    }
  },
  computed: {
    versionOptions() {
      return this.versions.map(v => ({ text: `Versão ${v.version}`, value: v.id }))
    }
  },
  async mounted() {
    await this.fetchVersions()
  },
  methods: {
    async fetchVersions() {
      try {
        const res = await this.$services.project.listVersions(this.$route.params.id)
        // Filtra para exibir apenas versões que já foram fechadas
        const versionsData = Array.isArray(res) ? res : (res.versions || [])
        this.versions = versionsData.filter(v => v.status === 'closed')
        if (this.versions.length) {
          this.selectedVersionId = this.versions[0].id
        }
      } catch (e) {
        console.error('Erro ao buscar versões:', e)
      }
    }
  }
}
</script> 