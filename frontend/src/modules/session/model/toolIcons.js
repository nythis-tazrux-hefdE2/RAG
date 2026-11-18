import {
  BookOpen,
  Calculator,
  FileEdit,
  FilePen,
  FileText,
  Folder,
  FolderOutput,
  FolderSearch,
  HelpCircle,
  SquareTerminal
} from '@lucide/vue'

export const TOOL_ICON_MAP = {
  ask_user_question: HelpCircle,








  bash: SquareTerminal,
  calculator: Calculator,
  cmd: SquareTerminal,
  edit_file: FilePen,
  execute: SquareTerminal,
  find_kb_document: FolderSearch,
  glob: FolderSearch,
  grep: FolderSearch,
  list_directory: Folder,
  list_kbs: BookOpen,
  ls: Folder,



  ocr_parse_file: FileText,
  open_kb_document: FileText,
  present_artifacts: FolderOutput,
  query_kb: BookOpen,
  read_file: FileText,

  replace: FilePen,
  run_shell_command: SquareTerminal,
  search_file: FolderSearch,
  search_file_content: FolderSearch,





  write_file: FileEdit
}

export const getToolIcon = (toolId) => TOOL_ICON_MAP[toolId] || null
