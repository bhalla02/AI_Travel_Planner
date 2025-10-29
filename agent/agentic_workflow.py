
from utils.model_loader import ModelLoader
from prompt_library.prompt import SYSTEM_PROMPT
from langgraph.graph import StateGraph, MessagesState, END, START
from langgraph.prebuilt import ToolNode, tools_condition
from tools.weather_info_tool import WeatherInfoTool
from tools.place_search_tool import PlaceSearchTool
from tools.expense_calculator_tool import CalculatorTool
from tools.currency_conversion_tool import CurrencyConverterTool

class GraphBuilder():
    def __init__(self,model_provider: str = "groq"):
        self.model_loader = ModelLoader(model_provider=model_provider)
        self.llm = self.model_loader.load_llm()
        
        self.tools = []
        
        self.weather_tools = WeatherInfoTool()
        self.place_search_tools = PlaceSearchTool()
        self.calculator_tools = CalculatorTool()
        self.currency_converter_tools = CurrencyConverterTool()
        
        self.tools.extend([* self.weather_tools.weather_tool_list, 
                           * self.place_search_tools.place_search_tool_list,
                           * self.calculator_tools.calculator_tool_list,
                           * self.currency_converter_tools.currency_converter_tool_list])
        
        self.llm_with_tools = self.llm.bind_tools(tools=self.tools)
        
        self.graph = None
        
        self.system_prompt = SYSTEM_PROMPT
    
    
    def agent_function(self, state: MessagesState):
        """Main agent function that processes the user query and returns a properly shaped message.

        LangChain expects messages to be dicts with at least 'role' and 'content' keys. Return
        a list with a single message dict so downstream code (and the frontend) won't see
        message coercion errors.
        """
        user_question = state["messages"]

        # Compose input with system prompt + user messages
        input_question = [self.system_prompt] + user_question

        # Invoke the LLM (may produce tool calls internally)
        response = self.llm_with_tools.invoke(input_question)

        # Normalize response into a dict with 'role' and 'content'
        message_dict = None

        # If response is an object with attributes 'role' and 'content'
        try:
            resp_role = getattr(response, "role", None)
            resp_content = getattr(response, "content", None)
        except Exception:
            resp_role = None
            resp_content = None

        if resp_content is not None:
            # response.content exists
            role = resp_role if resp_role else "assistant"
            content = resp_content
            message_dict = {"role": role, "content": content}
        else:
            # Fallback: coerce the whole response to string
            message_dict = {"role": "assistant", "content": str(response)}

        # Ensure we never return raw tool-call instructions — the system prompt should
        # have instructed the model to process tools, but if the content still contains
        # obvious tool call text, we can mask it with an informative line while allowing
        # the agent to continue processing in subsequent runs.
        content_lower = (message_dict.get("content") or "").lower()
        if any(p in content_lower for p in ["get current weather", "search transportation", "search attractions", "search restaurants"]):
            # provide a friendly intermediate message but keep proper shape
            message_dict = {"role": "assistant", "content": "Gathering live data to build your travel plan — please wait while I fetch details."}

        return {"messages": [message_dict]}
    def build_graph(self):
        graph_builder=StateGraph(MessagesState)
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START,"agent")
        graph_builder.add_conditional_edges("agent",tools_condition)
        graph_builder.add_edge("tools","agent")
        graph_builder.add_edge("agent",END)
        self.graph = graph_builder.compile()
        return self.graph
        
    def __call__(self):
        return self.build_graph()