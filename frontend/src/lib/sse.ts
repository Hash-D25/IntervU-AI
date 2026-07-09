import { ApiError } from "@/lib/api-client";

type SseEventBase = {
  stage: string;
  message?: string;
};

export async function readSseJsonStream<TEvent extends SseEventBase, TResult>(
  response: Response,
  onEvent: (event: TEvent) => void,
  options: {
    emptyStreamMessage: string;
    incompleteStreamMessage: string;
    errorStage?: string;
  },
): Promise<TResult> {
  if (!response.body) {
    throw new Error(options.emptyStreamMessage);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  const errorStage = options.errorStage ?? "error";

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";

    for (const chunk of chunks) {
      const line = chunk.trim();
      if (!line.startsWith("data: ")) {
        continue;
      }

      const event = JSON.parse(line.slice(6)) as TEvent & { result?: TResult };
      onEvent(event);

      if (event.stage === errorStage && event.message) {
        throw new ApiError(422, event.message);
      }
      if (event.stage === "done" && event.result !== undefined) {
        return event.result;
      }
    }
  }

  throw new Error(options.incompleteStreamMessage);
}
