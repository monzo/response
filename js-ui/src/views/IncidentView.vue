<template>
  <v-container fluid>
    <!-- summary -->
    <v-layout py-3>
      <v-flex>
      <v-card pa-5 ma-10>
        <v-card-title class="blue-grey lighten-4 bluegrey--text">
          <span class="title">#inc-kafka-down</span>
        </v-card-title>
        <v-card-text>
          <v-list subheader three-line>
            <v-list-tile>
              <v-list-tile-content>
                <v-list-tile-title>Summary</v-list-tile-title>
                <v-list-tile-sub-title>We saw that an Argentinian acquirer had submitted duplicate presentments for transactions made in February. Mastercard informed us that whilst there's a process for handling duplicate presentments for European acquirers, in this case we should submit chargebacks for the duplicates.</v-list-tile-sub-title>
              </v-list-tile-content>
            </v-list-tile>

            <v-list-tile>
              <v-list-tile-content>
                <v-list-tile-title>Impact</v-list-tile-title>
                <v-list-tile-sub-title>We've refunded customers for the amount of the presentments, and and we expect to win the chargebacks, but won't know for sure until the 45-day 2nd presentment window expires.</v-list-tile-sub-title>
              </v-list-tile-content>
            </v-list-tile>



            <v-list-tile>
              <v-list-tile-content>
                <v-list-tile-title>Notes</v-list-tile-title>
                <v-list-tile-sub-title>We have fixed the problem by acquiring the acquirer</v-list-tile-sub-title>
              </v-list-tile-content>
            </v-list-tile>

              <v-list-tile>
              <v-list-tile-content>
                <v-list-tile-title>Tags</v-list-tile-title>
                <v-list-tile-sub-title><v-chip>Kafka</v-chip><v-chip>payments</v-chip></v-list-tile-sub-title>
              </v-list-tile-content>
            </v-list-tile>
          </v-list>
        </v-card-text>
      </v-card>
    </v-flex>
    </v-layout>
    <!-- end summary -->
    <!-- timeline -->
    <v-layout py-3>
      <v-flex>
        <v-card>
          <v-card-title class="blue-grey lighten-4 bluegrey--text">
            <span class="title">Timeline - 2 hours</span>

            <v-spacer></v-spacer>
            <v-btn color="white" outline depressed class="ma-0">Add</v-btn>
          </v-card-title>
          <v-card-text class="py-0">
            <v-timeline dense>
              <v-timeline-item color="grey" small>
                <v-layout pt-3>
                  <v-flex xs3>
                    <strong>09:00 UTC</strong>
                  </v-flex>
                  <v-flex>
                    <strong>Incident opened</strong>
                    <div class="caption">Chris evans</div>
                  </v-flex>
                </v-layout>
              </v-timeline-item>
              <v-timeline-item color="grey" small>
                <v-layout pt-3>
                  <v-flex xs3>
                    <strong>10:45 UTC</strong>
                  </v-flex>
                  <v-flex>
                    <strong>I've restarted the server</strong>
                    <div class="caption">Guillaume Breton</div>
                  </v-flex>
                </v-layout>
              </v-timeline-item>
              <v-timeline-item color="green" small>
                <v-layout pt-3>
                  <v-flex xs3>
                    <strong>10:55 UTC</strong>
                  </v-flex>
                  <v-flex>
                    <strong>Incident closed</strong>
                    <div class="caption">Guillaume Breton</div>
                  </v-flex>
                </v-layout>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
    <!-- end timeline -->
    <!-- start actions -->
    <v-layout py-3>
      <v-flex>
        <v-card>
          <v-card-title class="blue-grey lighten-4 bluegrey--text">
            <span class="title">Actions</span>
            <v-spacer></v-spacer>
            <v-btn color="white" outline depressed class="ma-0">Add</v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table :headers="headers" :items="actions" hide-actions hide-headers>
              <template v-slot:items="props">
                <td>
                  <v-chip
                    color="{ getColor(props.item.done) }"
                    text-color="white"
                  >{{ props.item.done ? 'done' : 'pending' }}</v-chip>
                </td>
                <td>{{ props.item.description }}</td>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
    <!-- end actions -->
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { Incident } from "@/store/incidents";

@Component({})
export default class IncidentView extends Vue {
  headers: any[] = [
    { text: "Status" },
    {
      text: "Description"
    }
  ];
  actions: any[] = [
    {
      description: "Add a new server",
      done: true
    },
    {
      description: "Add a more tests",
      done: false
    },
    {
      description: "Add a more pods",
      done: true
    },
    {
      description: "Delete old config",
      done: false
    }
  ];

  getColor(value: boolean): string {
    if (value) {
      return "green";
    } else {
      return "red";
    }
  }
}
</script>
