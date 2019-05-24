<template>
  <v-app id="inspire">
    <Menu v-model="drawer"/>

    <v-toolbar color="indigo" dark fixed app clipped-left>
      <v-toolbar-side-icon @click.stop="toggle"></v-toolbar-side-icon>
      <v-toolbar-title>Incident-manager</v-toolbar-title>
    </v-toolbar>
    <v-content>

        <router-view/>
    </v-content>
  </v-app>
</template>



<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";
import { getModule } from "vuex-module-decorators";
import Menu from "@/components/Menu.vue"; // @ is an alias to /src

@Component({
  components: {
    Menu
  }
})
export default class App extends Vue {
  drawer: boolean = true;

  toggle() {
    this.drawer = !this.drawer;
  }
}
</script>

