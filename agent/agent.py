"""
LLM Agent for Movie Bot
Interacts with LLM to process movie-related queries
"""
import os
from typing import Optional
import anthropic
from mcp.client.stdio import StdioClientTransport
from mcp.client.session import ClientSession
import json


class MovieAgent:
    """Movie Bot Agent for interacting with LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the agent with Claude LLM"""
        self.client = anthropic.Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = os.getenv("MODEL", "claude-3-5-sonnet-20241022")
        self.tools = None
        self.mcp_session = None
    
    async def initialize_mcp(self):
        """Initialize MCP client connection"""
        try:
            # Transport for communicating with MCP server
            transport = StdioClientTransport(
                command="python",
                args=["-m", "mcp_server.server"],
                env=os.environ.copy()
            )
            
            self.mcp_session = ClientSession(transport)
            await self.mcp_session.__aenter__()
            
            # Get tools from MCP server
            tools_response = await self.mcp_session.list_tools()
            self.tools = tools_response.tools
            print(f"✓ Connected to MCP server with {len(self.tools)} tools")
            
        except Exception as e:
            print(f"Warning: Could not connect to MCP server: {e}")
            print("Agent will run without tool support")
    
    async def process_query(self, query: str, max_iterations: int = 10) -> str:
        """
        Process a user query using Claude and MCP tools
        """
        if not self.mcp_session:
            await self.initialize_mcp()
        
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]
        
        system_prompt = """You are a helpful movie assistant. You can help users find movies, 
        get recommendations, search for specific films, and provide information about cast, crew, 
        and ratings. Use the available tools to access the movie database and provide accurate information.
        
        When responding:
        1. Be concise and helpful
        2. Format information clearly
        3. If you don't find what the user is looking for, explain why
        4. Suggest alternatives when appropriate"""
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            # Create message with tools
            tool_definitions = []
            if self.tools:
                tool_definitions = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    }
                    for tool in self.tools
                ]
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                tools=tool_definitions if tool_definitions else None,
                messages=messages
            )
            
            # Check if we should stop
            if response.stop_reason == "end_turn":
                # Extract final text response
                for block in response.content:
                    if hasattr(block, 'text'):
                        return block.text
                return "No response generated"
            
            # Handle tool use
            if response.stop_reason == "tool_use":
                # Add assistant message to conversation
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Process each tool call
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        try:
                            # Call the MCP tool
                            tool_result = await self.mcp_session.call_tool(
                                block.name,
                                block.input
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(tool_result.content[0].text) 
                                           if tool_result.content else "No result"
                            })
                        except Exception as e:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Error: {str(e)}",
                                "is_error": True
                            })
                
                # Add tool results to messages
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                # Unexpected stop reason
                return "Agent stopped unexpectedly"
        
        return "Maximum iterations reached without a final response"
    
    async def chat(self, query: str) -> str:
        """
        Chat with the agent
        """
        try:
            response = await self.process_query(query)
            return response
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    async def summarize(self, text: str) -> str:
        """
        Summarize movie data or text
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"Please provide a concise summary of the following: {text}"
                }
            ]
        )
        
        for block in response.content:
            if hasattr(block, 'text'):
                return block.text
        
        return "Could not generate summary"
    
    async def improve_text(self, text: str) -> str:
        """
        Improve or enhance text (like movie descriptions)
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": f"Please improve and enhance the following text: {text}"
                }
            ]
        )
        
        for block in response.content:
            if hasattr(block, 'text'):
                return block.text
        
        return "Could not improve text"
    
    async def close(self):
        """Close MCP session"""
        if self.mcp_session:
            await self.mcp_session.__aexit__(None, None, None)


async def main():
    """Interactive chat with the movie agent"""
    agent = MovieAgent()
    
    print("🎬 Movie Bot Agent Started")
    print("Type 'quit' to exit, 'help' for commands\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                break
            
            if user_input.lower() == "help":
                print("""
Available commands:
- Regular queries: Ask about movies, get recommendations, search for films
- 'quit': Exit the agent
- 'help': Show this help message

Examples:
- "Find me action movies from 2020"
- "What are the top rated movies?"
- "Tell me about the movie Inception"
- "Give me some movie recommendations"
                """)
                continue
            
            print("\nAgent: Thinking...\n")
            response = await agent.chat(user_input)
            print(f"Agent: {response}\n")
        
        except KeyboardInterrupt:
            print("\nAgent stopped by user")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")
    
    await agent.close()
    print("Goodbye!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
