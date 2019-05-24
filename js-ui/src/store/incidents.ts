import store from '@/store'
import { Module, VuexModule, Mutation, Action } from 'vuex-module-decorators'

export class Incident {
    id: number
    summary: string
    date: string
    // report,
    // reporter,
    // report_time,
    // summary,
    // impact,
    // start_time,
    // end_time,
    // severity,
    // customers_impacted,
    // third_party,
    // impacted_product,
    // incident_type,
    // incident_thread_ts,
    // incident_channel_id,
    // incident_post_time,
    // comms_channel_id,
    // incident_lead,
    // on_call_engineers,
    // cops_activity_lead,
    // docs_url,
    // notes,
    // reviewer,
    // review_date,
    // redress,
    // costs,
    // reported_internally,
    // reported_to_regulator,
    // regulator_report_date, reported_as_operational_loss, regulatory_breach, notes

    constructor(id: number, date: string, summary: string) {
        this.id = id
        this.summary = summary
        this.date = date
    }
}

@Module({ name: 'incidents', store: store, dynamic:true, namespaced: true})
export default class IncidentsModule extends VuexModule {
    incidents: Incident[] = [
        new Incident(0, "2019-04-11","Incident #1"),
        new Incident(1, "2019-04-23","Incident #2"),
        new Incident(2, "2019-04-23","Incident #3"),
        new Incident(3, "2019-04-23","Incident #4"),
        new Incident(4,"2019-04-23","Incident #5")

    ]

    @Mutation
    setIncidents(payload: Incident[]) {
        this.incidents = payload
    }


    @Action({ commit: 'setIncidents' })
    fetch():Incident[]{
        console.log("fetch")
        return this.incidents
    }

}
