// TypeScript interface for the FileNode
export interface FileNode {
  file_path: string;
  connected_files: FileNode[];
  parent_files: FileNode[];
}

// TypeScript type for the details.
export type Detail = [string, number];

// TypeScript interface for the table data entry
export interface TableDataEntry {
  id: number;
  linkedId: number;
  file: FileNode;
  details: Detail[];
}
export type TableData = TableDataEntry[];

export interface TemplateDataEntry {
  id: number;
  template: Template;
}

export interface Template {
  all_main_file_paths_output: string;
  individual_outputs: string[];
}


const mockTableData: TableDataEntry[] = [
  {
    id:1,
    linkedId:1,
    file: {
      file_path: "/path/to/file1.ts",
      connected_files: [
        {
          file_path: "/path/to/file2.ts",
          connected_files: [],
          parent_files: []
        },
        {
          file_path: "/path/to/file3.ts",
          connected_files: [],
          parent_files: []
        }
      ],
      parent_files: []
    },
    details: [
      ["Detail1 for file1", 123],
      ["Detail2 for file1", 456]
    ]
  },
];

export default mockTableData;
