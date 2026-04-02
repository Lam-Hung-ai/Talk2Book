type PydanticError = { msg: string; loc?: (string | number)[] };

/**
 * Parse FastAPI/Pydantic error response to a plain string.
 * detail can be a string or an array of validation error objects.
 */
export async function parseApiError(res: Response, fallback = "Lỗi không xác định"): Promise<string> {
  try {
    const body = await res.json() as { detail?: string | PydanticError[] };
    const { detail } = body;
    if (!detail) return fallback;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((e) => {
          const field = e.loc ? e.loc.filter((l) => l !== "body").join(".") : "";
          return field ? `${field}: ${e.msg}` : e.msg;
        })
        .join("; ");
    }
    return fallback;
  } catch {
    return fallback;
  }
}
