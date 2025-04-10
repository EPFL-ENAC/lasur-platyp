import { defineStore } from 'pinia'
import { api } from 'src/boot/api'
import type { Entity, Company, CompanyAction, Campaign, Participant, Record } from 'src/models'
import type { Query } from 'src/components/models'

const authStore = useAuthStore()

export class Service<Type extends Company | CompanyAction | Campaign | Participant | Record> {
  constructor(
    public entityType: Type,
    public entityName: string,
  ) {}

  async create(payload: Type) {
    if (!authStore.isAuthenticated) return Promise.reject('Not authenticated')
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api.post(`/${this.entityName}/`, payload, config)
    })
  }

  async get(id: string): Promise<Type> {
    if (!authStore.isAuthenticated) return Promise.reject('Not authenticated')
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api.get(`/${this.entityName}/${id}`, config).then((res) => res.data)
    })
  }

  async find(query: Query | undefined) {
    if (!authStore.isAuthenticated) return Promise.reject('Not authenticated')
    const start = query?.$skip || 0
    const limit = query?.$limit || 10
    const range = [start, start + limit - 1]
    const sort = query?.$sort ? [query?.$sort[0], query?.$sort[1] ? 'DESC' : 'ASC'] : ['id', 'ASC']
    return authStore.updateToken().then(() => {
      return api
        .get(`/${this.entityName}/`, {
          headers: {
            Authorization: `Bearer ${authStore.accessToken}`,
          },
          params: {
            select: query?.$select ? JSON.stringify(query?.$select) : undefined,
            range: JSON.stringify(range),
            sort: JSON.stringify(sort),
            filter: JSON.stringify(query?.filter),
          },
        })
        .then((res) => res.data)
    })
  }

  async update(id: string | number, payload: Type) {
    if (!authStore.isAuthenticated) return Promise.reject('Not authenticated')
    delete (payload as Entity).created_at
    delete (payload as Entity).updated_at
    delete (payload as Entity).created_by
    delete (payload as Entity).updated_by
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api.put(`/${this.entityName}/${id}`, payload, config)
    })
  }

  async remove(id: string | number) {
    if (!authStore.isAuthenticated) return Promise.reject('Not authenticated')
    return authStore.updateToken().then(() => {
      const config = {
        headers: {
          Authorization: `Bearer ${authStore.accessToken}`,
        },
      }
      return api.delete(`/${this.entityName}/${id}`, config)
    })
  }
}

export const useServices = defineStore('services', () => {
  function make(
    entityName: string,
  ): Service<Company | CompanyAction | Campaign | Participant | Record> {
    let entityType
    switch (entityName) {
      case 'company':
        entityType = {} as Company
        break
      case 'action':
        entityType = {} as CompanyAction
        break
      case 'campaign':
        entityType = {} as Campaign
        break
      case 'participant':
        entityType = {} as Participant
        break
      case 'record':
        entityType = {} as Record
        break
    }
    if (!entityType) {
      throw new Error('Invalid entity name: ' + entityName)
    }
    return new Service(entityType, entityName)
  }

  return {
    make,
  }
})
