export function moveToEnd<T>(arr: T[], item: T | undefined) {
  if (item === undefined) return

  const index = arr.indexOf(item)
  if (index > -1) {
    arr.push(...arr.splice(index, 1))
  }
}

export function moveToStart<T>(arr: T[], item: T | undefined) {
  if (item === undefined) return

  const index = arr.indexOf(item)
  if (index > -1) {
    arr.unshift(...arr.splice(index, 1))
  }
}
