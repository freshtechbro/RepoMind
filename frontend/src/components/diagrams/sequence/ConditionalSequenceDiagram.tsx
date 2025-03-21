import React, { useEffect, useRef, useState } from 'react';
import * as joint from 'jointjs';

// Types for diagram data
interface Participant {
  name: string;
}

interface Message {
  from: string;
  to: string;
  method: string;
  args?: any[];
  is_conditional?: boolean;
  is_return?: boolean;
  in_conditional_block?: boolean;
  condition?: string;
  condition_type?: string;
  parent_condition?: string;
  loop_control?: 'break' | 'continue';
  code_snippet?: string;
  lineno?: number;
  id: string;
}

interface ConditionalBlock {
  start_message_id: string;
  end_message_id: string;
  condition: string;
  type: string;
  has_else: boolean;
  nesting_level: number;
  is_loop?: boolean;
}

export interface ConditionalSequenceDiagramData {
  participants: string[];
  messages: Message[];
  conditional_blocks: ConditionalBlock[];
  title?: string;
}

interface ConditionalSequenceDiagramProps {
  data: ConditionalSequenceDiagramData;
  width?: number;
  height?: number;
  onElementClick?: (elementId: string) => void;
}

const ConditionalSequenceDiagram: React.FC<ConditionalSequenceDiagramProps> = ({
  data,
  width = 800,
  height = 600,
  onElementClick
}) => {
  const paperRef = useRef<HTMLDivElement>(null);
  const [graph, setGraph] = useState<joint.dia.Graph | null>(null);
  const [paper, setPaper] = useState<joint.dia.Paper | null>(null);

  // Initialize JointJS graph and paper
  useEffect(() => {
    if (!paperRef.current) return;

    // Create a new graph
    const newGraph = new joint.dia.Graph();

    // Create a paper with grid
    const newPaper = new joint.dia.Paper({
      el: paperRef.current,
      model: newGraph,
      width: width,
      height: height,
      gridSize: 10,
      drawGrid: true,
      background: {
        color: '#f8f9fa'
      },
      interactive: true
    });

    // Set up event handler for clicks
    if (onElementClick) {
      newPaper.on('element:pointerclick', (elementView) => {
        onElementClick(elementView.model.id);
      });
    }

    setGraph(newGraph);
    setPaper(newPaper);

    // Cleanup on unmount
    return () => {
      newGraph.clear();
      newPaper.remove();
    };
  }, [paperRef, width, height, onElementClick]);

  // Render diagram when data changes
  useEffect(() => {
    if (!graph || !data) return;

    // Clear previous diagram
    graph.clear();

    // Define namespace for sequence diagram shapes
    const namespace = joint.shapes as any;
    if (!namespace.sequence) {
      namespace.sequence = {};
    }

    // Define custom shapes for sequence diagrams
    if (!namespace.sequence.Actor) {
      // Define Actor (Participant) shape
      namespace.sequence.Actor = joint.dia.Element.extend({
        markup: [
          '<g class="rotatable">',
          '<g class="scalable">',
          '<rect class="lifeline-head-rect"/></g>',
          '<text class="lifeline-head-text"/>',
          '<line class="lifeline-line"/>',
          '</g>'
        ].join(''),
        
        defaults: joint.util.defaultsDeep({
          type: 'sequence.Actor',
          size: { width: 100, height: 30 },
          attrs: {
            '.lifeline-head-rect': {
              fill: '#ffffff',
              stroke: '#000000',
              'stroke-width': 2,
              width: 100,
              height: 30
            },
            '.lifeline-head-text': {
              text: '',
              'font-size': 12,
              'text-anchor': 'middle',
              'ref-x': .5,
              'ref-y': .5,
              'y-alignment': 'middle',
              fill: '#000000'
            },
            '.lifeline-line': {
              x1: 50,
              y1: 30,
              x2: 50,
              y2: 1000,
              stroke: '#000000',
              'stroke-width': 1,
              'stroke-dasharray': '5,5'
            }
          }
        }, joint.dia.Element.prototype.defaults)
      });

      // Define Message shape with enhanced styling for conditional patterns
      namespace.sequence.Message = joint.dia.Link.extend({
        markup: [
          '<path class="connection" stroke="black" d="M 0 0 0 0"/>',
          '<path class="message-arrow" fill="black" stroke="black" d="M 0 0 0 0"/>',
          '<text class="message-text" font-size="12"/>',
        ].join(''),
        
        defaults: joint.util.defaultsDeep({
          type: 'sequence.Message',
          attrs: {
            '.connection': {
              'stroke-width': 1,
              'stroke': '#000000'
            },
            '.message-arrow': {
              'fill': '#000000',
              'stroke': '#000000'
            },
            '.message-text': {
              'text': '',
              'font-size': 12,
              'fill': '#000000'
            }
          },
          router: { name: 'orthogonal' },
          connector: { name: 'rounded' }
        }, joint.dia.Link.prototype.defaults)
      });

      // Define Activation box shape
      namespace.sequence.Activation = joint.dia.Element.extend({
        markup: '<rect class="activation-rect"/>',
        
        defaults: joint.util.defaultsDeep({
          type: 'sequence.Activation',
          size: { width: 10, height: 50 },
          attrs: {
            '.activation-rect': {
              fill: '#f5f5f5',
              stroke: '#000000',
              'stroke-width': 1,
              width: 10,
              height: 50
            }
          }
        }, joint.dia.Element.prototype.defaults)
      });
      
      // Define ConditionalBlock shape for showing conditional regions
      namespace.sequence.ConditionalBlock = joint.dia.Element.extend({
        markup: [
          '<rect class="conditional-region-rect"/>',
          '<text class="conditional-region-text"/>'
        ].join(''),
        
        defaults: joint.util.defaultsDeep({
          type: 'sequence.ConditionalBlock',
          size: { width: 150, height: 30 },
          attrs: {
            '.conditional-region-rect': {
              fill: 'rgba(255, 230, 200, 0.2)',
              stroke: '#dd8844',
              'stroke-dasharray': '5,3',
              'stroke-width': 1.5,
              rx: 5,
              ry: 5,
              width: 150,
              height: 30
            },
            '.conditional-region-text': {
              text: 'if condition',
              'font-size': 10,
              'text-anchor': 'middle',
              'ref-x': .5,
              'ref-y': 12,
              fill: '#dd8844'
            }
          }
        }, joint.dia.Element.prototype.defaults)
      });
      
      // Define LoopBlock shape for showing loop regions
      namespace.sequence.LoopBlock = joint.dia.Element.extend({
        markup: [
          '<rect class="loop-region-rect"/>',
          '<text class="loop-region-text"/>'
        ].join(''),
        
        defaults: joint.util.defaultsDeep({
          type: 'sequence.LoopBlock',
          size: { width: 150, height: 30 },
          attrs: {
            '.loop-region-rect': {
              fill: 'rgba(200, 255, 200, 0.2)',
              stroke: '#44bb77',
              'stroke-dasharray': '5,3',
              'stroke-width': 1.5,
              rx: 5,
              ry: 5,
              width: 150,
              height: 30
            },
            '.loop-region-text': {
              text: 'loop',
              'font-size': 10,
              'text-anchor': 'middle',
              'ref-x': .5,
              'ref-y': 12,
              fill: '#44bb77'
            }
          }
        }, joint.dia.Element.prototype.defaults)
      });
      
      // Define TryBlock shape for showing try-catch regions
      namespace.sequence.TryBlock = joint.dia.Element.extend({
        markup: [
          '<rect class="try-region-rect"/>',
          '<text class="try-region-text"/>'
        ].join(''),
        
        defaults: joint.util.defaultsDeep({
          type: 'sequence.TryBlock',
          size: { width: 150, height: 30 },
          attrs: {
            '.try-region-rect': {
              fill: 'rgba(200, 200, 255, 0.2)',
              stroke: '#5577cc',
              'stroke-dasharray': '5,3',
              'stroke-width': 1.5,
              rx: 5,
              ry: 5,
              width: 150,
              height: 30
            },
            '.try-region-text': {
              text: 'try',
              'font-size': 10,
              'text-anchor': 'middle',
              'ref-x': .5,
              'ref-y': 12,
              fill: '#5577cc'
            }
          }
        }, joint.dia.Element.prototype.defaults)
      });
    }

    // Render participants (actors)
    const actors: joint.dia.Element[] = [];
    const actorWidth = 100;
    const actorSpacing = 150;
    const actorY = 50;
    const lifelines: Record<string, { actor: joint.dia.Element, x: number }> = {};

    data.participants.forEach((participant, index) => {
      const x = index * actorSpacing + 100;
      
      const actor = new namespace.sequence.Actor({
        position: { x: x - (actorWidth / 2), y: actorY },
        attrs: {
          '.lifeline-head-text': { text: participant },
          '.lifeline-line': { y2: height - 50 }
        }
      });
      
      graph.addCell(actor);
      actors.push(actor);
      lifelines[participant] = { actor, x };
    });

    // Create lookup for message positions
    const messagePositions: { [id: string]: { x: number, y: number, fromX: number, toX: number } } = {};
    
    // Render messages
    const messageHeight = 50;
    let currentY = actorY + 50;

    data.messages.forEach((message, index) => {
      const fromLifeline = lifelines[message.from];
      const toLifeline = lifelines[message.to];
      
      if (!fromLifeline || !toLifeline) return;

      const fromX = fromLifeline.x;
      const toX = toLifeline.x;
      const isSelfMessage = message.from === message.to;
      
      // Create message link
      const messageLink = new namespace.sequence.Message({
        source: { x: fromX, y: currentY },
        target: { x: toX, y: currentY }
      });
      
      // Store position for use with conditional blocks
      messagePositions[message.id] = {
        x: (fromX + toX) / 2,
        y: currentY,
        fromX: fromX,
        toX: toX
      };

      // Set message text
      let messageText = message.method;
      if (message.args && message.args.length > 0) {
        messageText += `(${message.args.join(', ')})`;
      }
      
      messageLink.attr({
        '.message-text': {
          text: messageText,
          'ref-y': -10
        }
      });

      // Style for different message types
      if (message.is_return) {
        messageLink.attr({
          '.connection': {
            'stroke-dasharray': '3,3',
            'stroke': '#666666'
          },
          '.message-arrow': {
            'fill': '#666666',
            'stroke': '#666666'
          },
          '.message-text': {
            'fill': '#666666'
          }
        });
      }
      
      // Style for conditional messages
      if (message.is_conditional) {
        const color = _getColorForConditionType(message.condition_type || 'if');
        
        messageLink.attr({
          '.connection': {
            'stroke': color
          },
          '.message-arrow': {
            'fill': color,
            'stroke': color
          },
          '.message-text': {
            'text': `[${message.condition}] ${messageText}`,
            'fill': color,
            'font-weight': 'bold'
          }
        });
      }
      
      // Style for messages within conditional blocks
      if (message.in_conditional_block) {
        messageLink.attr({
          '.connection': {
            'stroke-dasharray': '2,2'
          }
        });
      }
      
      // Style for loop control messages (break/continue)
      if (message.loop_control) {
        const loopControlColor = message.loop_control === 'break' ? '#e74c3c' : '#3498db';
        
        messageLink.attr({
          '.connection': {
            'stroke': loopControlColor,
            'stroke-width': 2
          },
          '.message-arrow': {
            'fill': loopControlColor,
            'stroke': loopControlColor
          },
          '.message-text': {
            'text': `${message.loop_control}: ${messageText}`,
            'fill': loopControlColor,
            'font-weight': 'bold'
          }
        });
      }
      
      // Store the message ID as a property for later reference
      messageLink.prop('messageId', message.id);
      
      // Add to graph
      graph.addCell(messageLink);
      
      // Update current Y position for next message
      currentY += messageHeight;
    });
    
    // Render conditional blocks
    data.conditional_blocks.forEach(block => {
      const startPos = messagePositions[block.start_message_id];
      const endPos = messagePositions[block.end_message_id];
      
      if (!startPos || !endPos) return;
      
      // Calculate block dimensions
      const blockX = 50; // Left margin
      const blockY = startPos.y - 15; // Position above the start message
      const blockWidth = (data.participants.length - 1) * actorSpacing + 150;
      const blockHeight = (endPos.y - startPos.y) + 30; // Add padding
      
      // Create the appropriate block type
      let blockElement;
      
      if (block.is_loop) {
        // Loop block
        blockElement = new namespace.sequence.LoopBlock({
          position: { x: blockX, y: blockY },
          size: { width: blockWidth, height: blockHeight },
          attrs: {
            '.loop-region-text': { 
              text: `loop ${block.condition}`
            }
          }
        });
      } else if (block.type === 'try_except' || block.type === 'try_catch') {
        // Try-except/catch block
        blockElement = new namespace.sequence.TryBlock({
          position: { x: blockX, y: blockY },
          size: { width: blockWidth, height: blockHeight },
          attrs: {
            '.try-region-text': { 
              text: block.type === 'try_except' ? 'try-except' : 'try-catch'
            }
          }
        });
      } else {
        // Conditional block (if/else)
        blockElement = new namespace.sequence.ConditionalBlock({
          position: { x: blockX, y: blockY },
          size: { width: blockWidth, height: blockHeight },
          attrs: {
            '.conditional-region-text': { 
              text: `if ${block.condition}`
            }
          }
        });
        
        // Color based on nesting level
        const colors = ['#dd8844', '#dd6644', '#dd4444', '#cc4444', '#bb4444'];
        const color = colors[Math.min(block.nesting_level, colors.length - 1)];
        
        blockElement.attr({
          '.conditional-region-rect': {
            'stroke': color,
            'fill': `rgba(${255}, ${190 - block.nesting_level * 30}, ${160 - block.nesting_level * 30}, 0.2)`
          },
          '.conditional-region-text': {
            'fill': color
          }
        });
      }
      
      // Store block ID as a property
      blockElement.prop('blockId', `${block.start_message_id}_to_${block.end_message_id}`);
      
      // Add to graph behind other elements
      graph.addCell(blockElement);
      blockElement.toBack();
    });

  }, [graph, data, height]);

  /**
   * Get a color for a specific condition type
   */
  const _getColorForConditionType = (type: string): string => {
    switch (type) {
      case 'if_statement':
      case 'if_elif_chain':
        return '#dd8844';
      case 'ternary':
        return '#dd7744';
      case 'switch_case':
        return '#cc6677';
      case 'for_loop':
      case 'while_loop':
      case 'do_while_loop':
      case 'for_of_loop':
      case 'for_in_loop':
        return '#44bb77';
      case 'try_except':
      case 'try_catch':
        return '#5577cc';
      case 'if_break':
        return '#e74c3c';
      case 'if_continue':
        return '#3498db';
      default:
        return '#888888';
    }
  };

  return (
    <div className="conditional-sequence-diagram">
      <div ref={paperRef} className="diagram-paper" style={{ width, height }} />
    </div>
  );
};

export default ConditionalSequenceDiagram; 