<template>
  <v-container fluid>
    <v-layout row wrap>
      <v-flex xs12>
        <v-toolbar flat color="blue-grey white--text">
          <v-toolbar-title>Incidents</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn color="white" outline depressed @click="$refs.calendar.prev()">
            <v-icon>keyboard_arrow_left</v-icon>
          </v-btn>
          <v-btn color="white" outline depressed>
            <v-icon>today</v-icon>
          </v-btn>
          <v-btn color="white" outline depressed @click="$refs.calendar.next()">
            <v-icon>keyboard_arrow_right</v-icon>
          </v-btn>
        </v-toolbar>
      </v-flex>
    </v-layout>
    <v-layout row wrap fill-height>
      <v-flex d-flex xs12>
        <v-card class="primary" height="1000px">
          <v-calendar ref="calendar" color="primary" v-model="start" :type="type" :end="end">
            <template v-slot:day="{ date }">
              <template v-for="event in events[date]">
                <div
                  :key="event.id"
                  v-ripple
                  class="incident"
                  v-html="event.summary"
                  @click="displayIncident(event)"
                ></div>
              </template>
            </template>
          </v-calendar>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { getModule } from "vuex-module-decorators";
import IncidentsModule from "@/store/incidents";
import { Incident } from "@/store/incidents";
import router from "@/router";

const incidentsModule = getModule(IncidentsModule);

@Component({})
export default class IncidentList extends Vue {
  type: string = "month";
  start: string = "2019-04-01";
  end: string = "2019-04-30";
  mounted() {
    incidentsModule.fetch();
  }

  displayIncident(incident: Incident) {
    console.log("display incidents");
    router.push("/incidents/" + incident.id);
  }

  public get events(): Map<String, Incident[]> {
    let m: any = {};
    for (var i = 0; i < incidentsModule.incidents.length; i++) {
      let incident: Incident = incidentsModule.incidents[i];
      let arr = m[incident.date];
      if (arr) {
        arr.push(incident);
      } else {
        m[incident.date] = [incident];
      }
    }
    return m;
  }
}
</script>

<style lang="css" scoped>
.incident {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  border-radius: 2px;
  background-color: #1867c0;
  color: #ffffff;
  border: 1px solid #1867c0;
  width: 100%;
  font-size: 12px;
  padding: 3px;
  cursor: pointer;
  margin-bottom: 1px;
}
</style>
