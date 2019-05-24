<template>
  <v-navigation-drawer fixed clipped v-model="show" app>
    <v-list >
      <v-list-tile :to="{path: '/incidents'}">
        <v-list-tile-action>
          <v-icon>account_balance</v-icon>
        </v-list-tile-action>

        <v-list-tile-content>
          <v-list-tile-title>Incidents</v-list-tile-title>
        </v-list-tile-content>
        </v-list-tile>
     <v-list-tile :to="{path: '/export'}">
     <v-list-tile-action>
          <v-icon>import_export</v-icon>
        </v-list-tile-action>
        <v-list-tile-content>
          <v-list-tile-title>Export</v-list-tile-title>
        </v-list-tile-content>
      </v-list-tile>
    </v-list>

  </v-navigation-drawer>
</template>

<script lang="ts">
import { Component, Vue, Prop, Watch } from "vue-property-decorator";

@Component({})
export default class Menu extends Vue {
  @Prop({})
  value: boolean = true;

  show: boolean = true;

  @Watch("show")
  onChildChanged(val: boolean, oldVal: boolean) {
    this.$emit("input", val);
  }

  @Watch("value")
  onChildChanged2(val: boolean, oldVal: boolean) {
    this.show = val;
  }
}
</script>
