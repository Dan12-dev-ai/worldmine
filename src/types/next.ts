export interface NextApiRequest {
  query?: { [key: string]: string | string[] };
  body?: any;
  headers?: { [key: string]: string };
  method?: string;
}

export interface NextApiResponse<T = any> {
  statusCode?: number;
  status?: number;
  body?: T;
  headers?: { [key: string]: string };
}
