export function moveToEnd<T>(arr: T[], item: T) {
  const index = arr.indexOf(item);
  if (index > -1) {
    arr.push(...arr.splice(index, 1));
  }
}