import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'companies', component: () => import('pages/CompaniesPage.vue') },
      { path: 'company/:id', component: () => import('pages/CompanyPage.vue') },
      { path: 'records', component: () => import('pages/RecordsPage.vue') },
      { path: 'record/:id', component: () => import('pages/RecordPage.vue') },
      { path: 'users', component: () => import('pages/UsersPage.vue') },
    ],
  },
  {
    path: '/signin',
    component: () => import('pages/SigninPage.vue'),
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
