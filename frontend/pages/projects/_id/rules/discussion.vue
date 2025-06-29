<template>
  <v-card class="pa-4">
    <v-card-title>
      Discussão do Projeto
      <v-spacer />
      <v-btn color="secondary" @click="$router.back()">Voltar</v-btn>
    </v-card-title>
    <ProjectChat :project-id="$route.params.id" />
  </v-card>
</template>

<script>
import ProjectChat from '~/components/ProjectChat.vue'
export default {
  components: { ProjectChat },
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject']
}
</script> 