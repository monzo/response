import Vue from 'vue';
import Router from 'vue-router';
import IncidentList from './views/IncidentList.vue';
import IncidentView from './views/IncidentView.vue';

Vue.use(Router);

export default new Router({
    mode: 'history',
    base: process.env.BASE_URL,
    routes: [
        { path: '/', redirect: '/incidents' },
        {
            path: '/incidents',
            name: 'incidents',
            component: IncidentList,
        },
        {
            path: '/incidents/:id',
            name: 'incident',
            component: IncidentView,
            props: true,
        },
    ],
});
