import Vue from 'vue';
import Vuex, { StoreOptions } from 'vuex';
import CategoriesModule from '@/store/incidents';

Vue.use(Vuex);

export interface RootState {
    version: string;
    drawer: boolean;
}

const store: StoreOptions<RootState> = {
    state: {
        version: '1.0.0', // a simple property
        drawer: true
    },
    modules: {
        categories: CategoriesModule,
    }
};

export default new Vuex.Store<RootState>(store);
