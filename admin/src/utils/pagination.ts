import { notifyError } from './notify'

type PaginationProperties = {
  pagination: PaginationOptions
  filter?: string
}
type PaginationRequestHandler = (props: PaginationProperties) => void
type PaginationRequestFetcher = (
  startRow: number,
  fetchCount: number,
  filter: string,
  sortBy: string,
  descending: boolean,
) => Promise<PaginationFetchResult>
export type PaginationOptions = {
  sortBy: string
  descending: boolean
  page: number
  rowsPerPage: number
  rowsNumber?: number
}
type PaginationFetchResult = {
  total: number
}

export function makePaginationRequestHandler(
  fetchFromServer: PaginationRequestFetcher,
  pagination: Ref<PaginationOptions>,
): PaginationRequestHandler {
  return function (props) {
    const { page, rowsPerPage, sortBy, descending } = props.pagination
    const filter = props.filter

    // get all rows if "All" (0) is selected
    const fetchCount = rowsPerPage === 0 ? pagination.value.rowsNumber || 0 : rowsPerPage

    // calculate starting row of data
    const startRow = (page - 1) * rowsPerPage

    // fetch data from "server"
    fetchFromServer(startRow, fetchCount, filter || '', sortBy, descending)
      .then((result: PaginationFetchResult) => {
        pagination.value = { ...props.pagination, rowsNumber: result.total }
      })
      .catch(notifyError)
  }
}
