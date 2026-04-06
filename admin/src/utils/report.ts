import type { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'

export async function makeChartPage(
  chart: HTMLElement,
  text: string | undefined,
  doc: jsPDF,
  now: Date,
  brandName: string,
  title?: string,
  filterText?: string,
): Promise<boolean> {
  const margin = 15
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const maxWidth = pageWidth - 2 * margin
  const maxHeight = pageHeight - 4 * margin

  // Add title
  let topMargin = 15
  doc.setFontSize(18)
  doc.setTextColor(1, 152, 59) // Primary color #01983b
  doc.text(brandName, margin, topMargin)
  doc.setTextColor(0, 0, 0) // Reset to black
  if (title) {
    doc.setFontSize(12)
    doc.text(title || '', pageWidth - margin, topMargin, { align: 'right' })
  }

  topMargin = pageHeight - 15
  doc.setFontSize(10)
  doc.text(now.toLocaleString(), margin, topMargin)
  if (filterText) {
    doc.text(filterText, pageWidth - margin, topMargin, { align: 'right' })
  }

  try {
    const canvas = await html2canvas(chart, {
      scale: 2,
      logging: false,
      useCORS: true,
      backgroundColor: '#ffffff',
    })

    const imgData = canvas.toDataURL('image/png')
    const imgWidth = canvas.width
    const imgHeight = canvas.height
    const ratio = imgWidth / imgHeight

    // Logic for Text Wrapping
    let textLines: string[] = []
    let textBlockHeight = 0
    const lineHeight = 5 // Adjust based on font size

    if (text) {
      doc.setFontSize(10)
      const safeText = toPdfSafeText(text)
      // Split text to fit the maxWidth
      textLines = doc.splitTextToSize(safeText, maxWidth)
      textBlockHeight = textLines.length * lineHeight
    }

    const heightOffset = textBlockHeight + 10 // 10 for spacing between chart and text

    // Calculate dimensions to fit the page
    let finalHeight = maxHeight - heightOffset // margin for the text
    let finalWidth = finalHeight * ratio

    if (finalWidth > maxWidth) {
      finalWidth = maxWidth
      finalHeight = finalWidth / ratio
    }

    // Center the image on the page
    const x = (pageWidth - finalWidth) / 2
    const y = margin + 20 // (pageHeight - finalHeight) / 2

    doc.addImage(imgData, 'PNG', x, y, finalWidth, finalHeight)
    if (textLines.length > 0) {
      doc.text(textLines, margin, pageHeight - margin - heightOffset)
    }
    return true
  } catch (error) {
    console.error('Error capturing chart:', error)
    return false
  }
}

function toPdfSafeText(text: string) {
  return text
    .normalize('NFKD')
    .replace(/[‘’]/g, "'")
    .replace(/[“”]/g, '"')
    .replace(/[–—]/g, '-')
    .replace(/\s+/g, ' ')
    .trim()
}
