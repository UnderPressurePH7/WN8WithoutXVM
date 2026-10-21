package com.under_pressure.WN8WithoutXVM.battle
{
   import flash.display.DisplayObject;
   import flash.display.DisplayObjectContainer;
   import flash.display.Sprite;
   import flash.events.Event;
   import flash.filters.ColorMatrixFilter;
   import flash.filters.DropShadowFilter;
   import flash.geom.ColorTransform;
   import flash.geom.Point;
   import flash.text.AntiAliasType;
   import flash.text.TextField;
   import flash.text.TextFieldAutoSize;
   import flash.text.TextFormat;
   import flash.utils.Dictionary;

   import com.under_pressure.WN8WithoutXVM.injector.BattleDisplayable;
   import com.under_pressure.WN8WithoutXVM.utils.Utils;

   import net.wg.data.constants.generated.PLAYERS_PANEL_STATE;
   import net.wg.gui.battle.components.BattleAtlasSprite;
   import net.wg.gui.battle.views.stats.fullStats.FullStatsTableBase;

   import scaleform.gfx.TextFieldEx;

   /**
    * WN8 overlay for the supported battle families.
    *
    * WG uses different battle-page classes per mode.  Classic/Stronghold and
    * Comp7 expose `playersPanel`; Epic Random/Frontline exposes
    * `epicRandomPlayersPanel`.  The component therefore resolves the panel by
    * capability instead of casting the page to random.views.BattlePage.
    */
   public class playerPanel extends BattleDisplayable
   {
      private static const POOL_SIZE:int = 96;
      // Gap between the stock vehicle-name field and the statistics column.
      private static const TAB_OVERLAY_OFFSET_X:Number = 80;
      private static const TAB_COLUMN_WIDTH:Number = 56;
      private static const TAB_COLUMN_GAP:Number = 2;
      private static const TAB_COLUMN_COUNT:int = 3;
      private static const TAB_OVERLAY_WIDTH:Number =
         TAB_COLUMN_WIDTH * TAB_COLUMN_COUNT +
         TAB_COLUMN_GAP * (TAB_COLUMN_COUNT - 1);

      private var _textFieldPool:Vector.<TextField>;
      private var _defaultTextFormat:TextFormat;
      private var _containers:Dictionary;
      private var _vehicleTextFields:Dictionary;
      private var _tabOverlayTextFields:Vector.<TextField>;
      private var _tabOverlayHeaderFields:Vector.<TextField>;
      private var _cachedShadows:Dictionary;
      private var _panelTextColors:Dictionary;
      private var _panelTextBaseFilters:Dictionary;
      private var _stockTextStats:Dictionary;
      private var _stockFieldRecords:Dictionary;
      private var _hiddenSquadIcons:Dictionary;
      private var _stockOverlayLayer:Sprite;
      private var _statsCacheMgr:StatisticDataCache;
      private var _eventListeners:Vector.<BattleAtlasSprite>;
      private var _currentPanelState:int = -1;
      private var _isDisposed:Boolean = false;

      public var flashLogS:Function;

      public function playerPanel()
      {
         super();
         name = "playerPanel";

         this._textFieldPool = new Vector.<TextField>();
         this._defaultTextFormat = new TextFormat(
            "$UniversCondC", 14, 0xFFFFFF, false, false, false,
            "", "", "left", 0, 0, 0, 0
         );
         this._containers = new Dictionary();
         this._vehicleTextFields = new Dictionary();
         // Dynamic sizing supports the different fixed-size FullStats tables.
         // Frontline uses a separate scrolling-list implementation.
         this._tabOverlayTextFields = new Vector.<TextField>();
         this._tabOverlayHeaderFields = new Vector.<TextField>();
         this._cachedShadows = new Dictionary();
         this._panelTextColors = new Dictionary();
         this._panelTextBaseFilters = new Dictionary(true);
         this._stockTextStats = new Dictionary();
         this._stockFieldRecords = new Dictionary(true);
         this._hiddenSquadIcons = new Dictionary(true);
         this._stockOverlayLayer = new Sprite();
         this._stockOverlayLayer.mouseEnabled = false;
         this._stockOverlayLayer.mouseChildren = false;
         this._eventListeners = new Vector.<BattleAtlasSprite>();

         this._statsCacheMgr = StatisticDataCache.getInstance();
         this._statsCacheMgr.addEventListener(
            StatisticDataEvent.CYCLIC_STATS_RECEIVED,
            this.onStatsReceived,
            false,
            0,
            true
         );

         for (var i:int = 0; i < POOL_SIZE; i++)
         {
            this._textFieldPool.push(this.createTextField());
         }
      }

      private function createTextField():TextField
      {
         var tf:TextField = new TextField();
         TextFieldEx.setNoTranslate(tf, true);
         tf.defaultTextFormat = this._defaultTextFormat;
         tf.mouseEnabled = false;
         tf.background = false;
         tf.embedFonts = true;
         tf.multiline = false;
         tf.selectable = false;
         tf.tabEnabled = false;
         tf.antiAliasType = AntiAliasType.ADVANCED;
         return tf;
      }

      private function acquireTextField():TextField
      {
         return this._textFieldPool.length > 0
            ? this._textFieldPool.pop()
            : this.createTextField();
      }

      private function releaseTextField(tf:TextField):void
      {
         if (!tf) return;
         tf.text = "";
         tf.htmlText = "";
         tf.filters = null;
         tf.alpha = 1;
         tf.visible = true;
         tf.transform.colorTransform = new ColorTransform();
         if (tf.parent) tf.parent.removeChild(tf);
         if (!this._isDisposed && this._textFieldPool.length < POOL_SIZE)
         {
            this._textFieldPool.push(tf);
         }
      }

      private function getMember(target:*, memberName:String):*
      {
         if (!target) return null;
         try
         {
            return target[memberName];
         }
         catch (e:Error) { }
         return null;
      }

      /** Resolve Classic/Stronghold/Comp7 and Epic Random/Frontline panels. */
      private function resolvePlayersPanel():*
      {
         var page:* = this.battlePage;
         if (!page) return null;

         var panel:* = this.getMember(page, "playersPanel");
         if (panel) return panel;

         panel = this.getMember(page, "epicRandomPlayersPanel");
         if (panel) return panel;

         return null;
      }

      private function resolveFullStats():*
      {
         try
         {
            var page:* = this.battlePage;
            if (!page) return null;
            if (page.hasOwnProperty("fullStats") && page["fullStats"])
               return page["fullStats"];
            if (page.hasOwnProperty("tabScreen") && page["tabScreen"])
               return page["tabScreen"];
         }
         catch (e:Error)
         {
            this.logError("resolveFullStats: " + e.message);
         }
         return null;
      }

      private function getHolder(list:*, vehicleID:int):*
      {
         if (!list) return null;

         try
         {
            return list.getHolderByVehicleID(vehicleID);
         }
         catch (e:Error) { }

         try
         {
            return list.getHolderByVehicleId(vehicleID);
         }
         catch (e2:Error) { }

         return null;
      }

      private function getListItemFromHolder(holder:*):*
      {
         if (!holder) return null;

         try
         {
            return holder.getListItem();
         }
         catch (e:Error) { }

         var item:* = this.getMember(holder, "_listItem");
         if (item) return item;

         return this.getMember(holder, "listItem");
      }

      public function getPPListItem(vehicleID:int):*
      {
         var panel:* = this.resolvePlayersPanel();
         if (!panel) return null;

         try
         {
            var holder:*;
            var listRight:* = this.getMember(panel, "listRight");
            if (listRight)
            {
               holder = this.getHolder(listRight, vehicleID);
               if (holder) return this.getListItemFromHolder(holder);
            }

            var listLeft:* = this.getMember(panel, "listLeft");
            if (listLeft)
            {
               holder = this.getHolder(listLeft, vehicleID);
               if (holder) return this.getListItemFromHolder(holder);
            }
         }
         catch (e:Error)
         {
            this.logError("getPPListItem: " + e.message);
         }
         return null;
      }

      private function isPPEnemy(vehicleID:int):Boolean
      {
         var panel:* = this.resolvePlayersPanel();
         if (!panel) return false;
         var listRight:* = this.getMember(panel, "listRight");
         return listRight && this.getHolder(listRight, vehicleID) != null;
      }

      private function getShadow(config:Object):DropShadowFilter
      {
         if (!config) return null;
         var key:String = String(config.distance) + "_" + String(config.angle) + "_" +
            String(config.color) + "_" + String(config.alpha) + "_" +
            String(config.size) + "_" + String(config.strength);
         if (!this._cachedShadows[key])
         {
            this._cachedShadows[key] = Utils.getDropShadowFilter(
               config.distance, config.angle, config.color,
               config.alpha, config.size, config.strength
            );
         }
         return this._cachedShadows[key] as DropShadowFilter;
      }

      private function getPositionConfig(container:Object, enemy:Boolean):Object
      {
         return container ? container[enemy ? "right" : "left"] : null;
      }

      private function createPPTextField(containerName:String, vehicleID:int, container:Object):TextField
      {
         var item:* = this.getPPListItem(vehicleID);
         if (!item) return null;

         var tf:TextField = this.acquireTextField();
         var childName:String = container.hasOwnProperty("child") ? String(container.child) : "";
         var child:DisplayObject = childName
            ? this.getMember(item, childName) as DisplayObject
            : null;

         if (child && item is DisplayObjectContainer)
         {
            DisplayObjectContainer(item).addChildAt(
               tf,
               DisplayObjectContainer(item).getChildIndex(child) + 1
            );
         }
         else if (item is DisplayObjectContainer)
         {
            DisplayObjectContainer(item).addChild(tf);
         }
         else
         {
            this.releaseTextField(tf);
            return null;
         }

         var enemy:Boolean = this.isPPEnemy(vehicleID);
         var pos:Object = this.getPositionConfig(container, enemy);
         tf.width = pos && pos.hasOwnProperty("width") ? Number(pos.width) : 80;
         tf.height = pos && pos.hasOwnProperty("height") ? Number(pos.height) : 20;
         var align:String = pos && pos.hasOwnProperty("align") ? String(pos.align) : "left";
         tf.autoSize = align == "right"
            ? TextFieldAutoSize.RIGHT
            : (align == "center" ? TextFieldAutoSize.CENTER : TextFieldAutoSize.LEFT);

         if (container.hasOwnProperty("shadow") && container.shadow)
            tf.filters = [this.getShadow(container.shadow)];

         var fields:Dictionary = this._vehicleTextFields[containerName] as Dictionary;
         if (!fields)
         {
            fields = new Dictionary();
            this._vehicleTextFields[containerName] = fields;
         }
         fields[vehicleID] = tf;
         this.updatePPTextFieldPosition(containerName, vehicleID, tf, container);
         return tf;
      }

      private function updatePPTextFieldPosition(
         containerName:String,
         vehicleID:int,
         tf:TextField,
         container:Object
      ):void
      {
         var item:* = this.getPPListItem(vehicleID);
         if (!item || !tf || !container) return;

         var enemy:Boolean = this.isPPEnemy(vehicleID);
         var pos:Object = this.getPositionConfig(container, enemy);
         if (!pos) return;

         var baseX:Number = 0;
         var baseY:Number = 0;
         var anchor:DisplayObject = null;
         var holderName:String = container.hasOwnProperty("holder") ? String(container.holder) : "";
         if (holderName)
         {
            anchor = this.getMember(item, holderName) as DisplayObject;
            if (anchor)
            {
               baseX = anchor.x;
               baseY = anchor.y;
            }
         }

         var offsetX:Number = pos.hasOwnProperty("x") ? Number(pos.x) : 0;
         var offsetY:Number = pos.hasOwnProperty("y") ? Number(pos.y) : 0;
         if (anchor && pos.hasOwnProperty("anchorEdge"))
            baseX = this.resolveAnchorEdgeX(anchor, String(pos.anchorEdge));
         var state:int = item.hasOwnProperty("state") ? int(item.state) : this._currentPanelState;
         var usingFallback:Boolean = false;
         var isFullPanel:Boolean =
            state == PLAYERS_PANEL_STATE.FULL ||
            state == PLAYERS_PANEL_STATE.FULL_NO_BADGES;

         if (container.hasOwnProperty("hideWithHolder") && Boolean(container.hideWithHolder) &&
             (!isFullPanel || !this.isUsableTextAnchor(anchor)) &&
             container.hasOwnProperty("fallbackHolder"))
         {
            var fallbackName:String = String(container.fallbackHolder);
            var fallbackAnchor:DisplayObject = this.getMember(item, fallbackName) as DisplayObject;
            if (fallbackAnchor)
            {
               anchor = fallbackAnchor;
               baseX = fallbackAnchor.x;
               baseY = fallbackAnchor.y;
               if (pos.hasOwnProperty("fallbackAnchorEdge"))
                  baseX = this.resolveAnchorEdgeX(
                     fallbackAnchor, String(pos.fallbackAnchorEdge)
                  );
               offsetX = pos.hasOwnProperty("fallbackX") ? Number(pos.fallbackX) : offsetX;
               offsetY = pos.hasOwnProperty("fallbackY") ? Number(pos.fallbackY) : offsetY;
               usingFallback = true;
            }
         }

         if (!usingFallback && pos.hasOwnProperty("stateOffsets") && pos.stateOffsets && state >= 0)
         {
            var stateKey:String = "state" + String(state);
            if (pos.stateOffsets.hasOwnProperty(stateKey))
            {
               var stateOffset:Object = pos.stateOffsets[stateKey];
               if (stateOffset.hasOwnProperty("x")) offsetX = Number(stateOffset.x);
               if (stateOffset.hasOwnProperty("y")) offsetY = Number(stateOffset.y);
            }
         }

         tf.x = baseX + offsetX;
         tf.y = baseY + offsetY;
         tf.visible = state != PLAYERS_PANEL_STATE.HIDDEN;

         var activeAlign:String = usingFallback && pos.hasOwnProperty("fallbackAlign")
            ? String(pos.fallbackAlign)
            : (pos.hasOwnProperty("align") ? String(pos.align) : "left");
         tf.autoSize = activeAlign == "right"
            ? TextFieldAutoSize.RIGHT
            : (activeAlign == "center" ? TextFieldAutoSize.CENTER : TextFieldAutoSize.LEFT);

         if (tf.visible && container.hasOwnProperty("hideWithHolder") &&
             Boolean(container.hideWithHolder))
         {
            tf.visible = this.isUsableTextAnchor(anchor);
         }

         if (tf.visible && pos.hasOwnProperty("hideInStates") && pos.hideInStates)
         {
            for each (var hiddenState:int in pos.hideInStates as Array)
            {
               if (hiddenState == state)
               {
                  tf.visible = false;
                  break;
               }
            }
         }
      }

      private function isUsableTextAnchor(anchor:DisplayObject):Boolean
      {
         if (!anchor || !anchor.visible) return false;
         var textField:TextField = anchor as TextField;
         return !textField || (textField.text != null && textField.text.length > 0);
      }

      private function resolveAnchorEdgeX(anchor:DisplayObject, edge:String):Number
      {
         if (!anchor) return 0;
         if (edge == "right") return anchor.x + anchor.width;
         if (edge != "textLeft" && edge != "textRight") return anchor.x;

         var textField:TextField = anchor as TextField;
         if (!textField) return edge == "textRight" ? anchor.x + anchor.width : anchor.x;

         var glyphWidth:Number = Math.min(
            textField.width,
            Math.max(0, textField.textWidth + 4)
         );
         var glyphLeft:Number = textField.x;
         var format:TextFormat = textField.getTextFormat();
         var align:String = format && format.align ? String(format.align) : "left";
         if (align == "right")
            glyphLeft = textField.x + textField.width - glyphWidth;
         else if (align == "center")
            glyphLeft = textField.x + (textField.width - glyphWidth) * 0.5;

         return edge == "textRight" ? glyphLeft + glyphWidth : glyphLeft;
      }

      private function onStatsReceived(event:StatisticDataEvent):void
      {
         if (this._isDisposed) return;
         var data:Object = this._statsCacheMgr.getStatsData(event.vehicleID);
         if (!data) return;
         for (var containerName:String in this._containers)
            this.updateVehicleData(containerName, event.vehicleID, data);
      }

      private function updateVehicleData(containerName:String, vehicleID:int, data:Object):void
      {
         var container:Object = this._containers[containerName];
         if (!container) return;
         if (container.hasOwnProperty("stockTextInjection") &&
             Boolean(container.stockTextInjection)) return;

         var fields:Dictionary = this._vehicleTextFields[containerName] as Dictionary;
         var tf:TextField = fields ? fields[vehicleID] as TextField : null;
         if (!tf) tf = this.createPPTextField(containerName, vehicleID, container);
         if (!tf) return;

         var textKey:String = container.hasOwnProperty("textKey") && container.textKey
            ? String(container.textKey)
            : containerName;
         var sideKey:String = textKey + (this.isPPEnemy(vehicleID) ? "_right" : "_left");
         if (data.hasOwnProperty(sideKey)) tf.htmlText = String(data[sideKey]);
         else if (data.hasOwnProperty(textKey)) tf.htmlText = String(data[textKey]);
         tf.visible = tf.htmlText.length > 0;
      }

      public function as_setStatsData(vehicleID:int, data:Object):void
      {
         if (!data || this._isDisposed) return;
         this._statsCacheMgr.addStatsData(vehicleID, data);
      }

      public function as_create(containerName:String, config:Object):void
      {
         if (!containerName || !config || this._isDisposed) return;
         this._containers[containerName] = config;
         this._vehicleTextFields[containerName] = new Dictionary();
      }

      public function as_update(containerName:String, data:Object):void
      {
         if (!containerName || !data || !data.hasOwnProperty("vehicleID")) return;
         var vehicleID:int = int(data.vehicleID);
         var container:Object = this._containers[containerName];
         if (!container) return;
         if (container.hasOwnProperty("stockTextInjection") &&
             Boolean(container.stockTextInjection))
         {
            if (data.hasOwnProperty("text") && String(data.text).length > 0)
               this._stockTextStats[vehicleID] = String(data.text);
            else
               delete this._stockTextStats[vehicleID];
            this.applyStockTextStat(vehicleID);
            return;
         }
         var fields:Dictionary = this._vehicleTextFields[containerName] as Dictionary;
         var tf:TextField = fields ? fields[vehicleID] as TextField : null;
         if (!tf) tf = this.createPPTextField(containerName, vehicleID, container);
         if (tf && data.hasOwnProperty("text"))
         {
            tf.htmlText = String(data.text);
            tf.visible = tf.htmlText.length > 0;
         }
      }

      public function as_delete(containerName:String):void
      {
         var container:Object = this._containers[containerName];
         if (container && container.hasOwnProperty("stockTextInjection") &&
             Boolean(container.stockTextInjection))
         {
            this.restoreAllStockTextFields();
            this.restoreStockSquadIcons();
            this._stockTextStats = new Dictionary();
         }
         var fields:Dictionary = this._vehicleTextFields[containerName] as Dictionary;
         if (fields)
         {
            for each (var tf:TextField in fields) this.releaseTextField(tf);
         }
         delete this._vehicleTextFields[containerName];
         delete this._containers[containerName];
      }

      public function as_hasOwnProperty(containerName:String):Boolean
      {
         return containerName && this._containers[containerName] != null;
      }

      public function as_updatePosition(containerName:String, vehicleID:int):void
      {
         var container:Object = this._containers[containerName];
         if (container && container.hasOwnProperty("stockTextInjection") &&
             Boolean(container.stockTextInjection))
         {
            this.applyStockTextStat(vehicleID);
            return;
         }
         var fields:Dictionary = this._vehicleTextFields[containerName] as Dictionary;
         var tf:TextField = fields ? fields[vehicleID] as TextField : null;
         if (tf) this.updatePPTextFieldPosition(
            containerName,
            vehicleID,
            tf,
            this._containers[containerName]
         );
      }

      public function as_updateAllPositions():void
      {
         this.updateStockOverlayVisibility();
         for (var name:String in this._vehicleTextFields)
         {
            var fields:Dictionary = this._vehicleTextFields[name] as Dictionary;
            for (var vehicleID:* in fields)
               this.updatePPTextFieldPosition(name, int(vehicleID), fields[vehicleID], this._containers[name]);
         }
         for (var statVehicleID:* in this._stockTextStats)
            this.applyStockTextStat(int(statVehicleID));
      }

      public function as_setPanelState(state:int):void
      {
         this._currentPanelState = state;
         this.as_updateAllPositions();
      }

      public function as_clearCache():void
      {
         if (this._statsCacheMgr) this._statsCacheMgr.clear();
      }

      public function as_getPPListItem(vehicleID:int):*
      {
         return this.getPPListItem(vehicleID);
      }

      public function as_getPlayersPanel():*
      {
         return this.resolvePlayersPanel();
      }

      public function as_getVehicleTFPositions(vehicleIDs:Array):Array
      {
         var result:Array = [];
         if (!vehicleIDs) return result;

         for each (var vehicleID:int in vehicleIDs)
         {
            var item:* = this.getPPListItem(vehicleID);
            if (!item || !item.hasOwnProperty("vehicleTF") || !item.vehicleTF) continue;
            var vehicleTF:* = item.vehicleTF;
            var point:Point = vehicleTF.localToGlobal(new Point(0, 0));
            var itemPoint:Point = item.localToGlobal(new Point(0, 0));
            var stageWidth:Number = stage ? stage.stageWidth : 1920;
            result.push({
               vehicleID: vehicleID,
               x: point.x,
               y: point.y,
               w: vehicleTF.width,
               h: vehicleTF.height,
               side: itemPoint.x < stageWidth * 0.5 ? "left" : "right",
               visible: vehicleTF.visible && item.visible
            });
         }
         return result;
      }

      public function as_vehicleIconColor(vehicleID:int, colorStr:String):void
      {
         var item:* = this.getPPListItem(vehicleID);
         if (!item || !item.hasOwnProperty("vehicleIcon")) return;
         var icon:BattleAtlasSprite = item.vehicleIcon as BattleAtlasSprite;
         if (!icon) return;

         icon["playerPanel"] = {color: Utils.colorConvert(colorStr)};
         if (!icon.hasEventListener(Event.RENDER))
         {
            icon.addEventListener(Event.RENDER, this.onRenderHandle, false, 0, true);
            this._eventListeners.push(icon);
         }
         this.applyIconColor(icon);
      }

      public function as_vehicleNameColor(vehicleID:int, colorStr:String, vehicleName:String):void
      {
         this.as_setPanelTextColor(vehicleID, colorStr);
      }

      public function as_setPanelTextColor(vehicleID:int, colorStr:String):void
      {
         if (!vehicleID || this._isDisposed) return;
         if (colorStr)
         {
            this._panelTextColors[vehicleID] = colorStr;
            this.applyPanelTextColor(vehicleID);
         }
         else
         {
            delete this._panelTextColors[vehicleID];
            this.restorePanelTextColor(vehicleID);
         }
      }

      private function ensureStockOverlayLayer():Sprite
      {
         if (!this._stockOverlayLayer) return null;
         var panel:DisplayObject = this.resolvePlayersPanel() as DisplayObject;
         if (!panel || !panel.parent) return null;
         var parent:DisplayObjectContainer = panel.parent;
         if (this._stockOverlayLayer.parent != parent)
         {
            if (this._stockOverlayLayer.parent)
               this._stockOverlayLayer.parent.removeChild(this._stockOverlayLayer);
            var panelIndex:int = parent.getChildIndex(panel);
            parent.addChildAt(
               this._stockOverlayLayer,
               Math.min(panelIndex + 1, parent.numChildren)
            );
         }
         return this._stockOverlayLayer;
      }

      private function updateStockOverlayVisibility():void
      {
         var layer:Sprite = this.ensureStockOverlayLayer();
         if (!layer) return;
         var panel:DisplayObject = this.resolvePlayersPanel() as DisplayObject;
         var fullStats:DisplayObject = this.resolveFullStats() as DisplayObject;
         layer.visible = panel && panel.visible && !(fullStats && fullStats.visible);
      }

      private function restoreStockTextField(tf:TextField):void
      {
         if (!tf || !this._stockFieldRecords) return;
         var record:Object = this._stockFieldRecords[tf];
         if (!record) return;
         if (tf.htmlText == record.injectedHtml)
            tf.htmlText = record.originalHtml;
         delete this._stockFieldRecords[tf];
      }

      private function restoreAllStockTextFields():void
      {
         if (!this._stockFieldRecords) return;
         var fields:Array = [];
         for (var field:* in this._stockFieldRecords) fields.push(field);
         for each (var tf:TextField in fields) this.restoreStockTextField(tf);
      }

      private function applyStockTextStat(vehicleID:int):void
      {
         this.updateStockOverlayVisibility();
         var item:* = this.getPPListItem(vehicleID);
         if (!item) return;
         this.hideStockSquadIcon(item);

         var vehicleTF:TextField = this.getMember(item, "vehicleTF") as TextField;
         var statHtml:String = this._stockTextStats[vehicleID] as String;

         var fields:Dictionary = this._vehicleTextFields["wn8withoutxvm_pp_winrate"] as Dictionary;
         if (!fields) return;
         var statTF:TextField = fields[vehicleID] as TextField;
         if (!statHtml || !item.visible)
         {
            if (statTF) statTF.visible = false;
            return;
         }

         if (!statTF)
         {
            var layer:Sprite = this.ensureStockOverlayLayer();
            if (!layer) return;
            statTF = this.acquireTextField();
            statTF.autoSize = TextFieldAutoSize.LEFT;
            layer.addChild(statTF);
            fields[vehicleID] = statTF;
         }
         statTF.htmlText = statHtml;
         statTF.visible = true;

         var rowPoint:Point = vehicleTF
            ? vehicleTF.localToGlobal(new Point(0, 0))
            : DisplayObject(item).localToGlobal(new Point(0, 0));
         var screenWidth:Number = stage ? stage.stageWidth : 1920;
         var edge:Number = 2;
         var enemy:Boolean = this.isPPEnemy(vehicleID);
         var globalX:Number = enemy
            ? screenWidth - edge - statTF.width
            : edge;
         var overlay:Sprite = this.ensureStockOverlayLayer();
         if (!overlay) return;
         if (statTF.parent != overlay) overlay.addChild(statTF);
         var localPoint:Point = overlay.globalToLocal(new Point(globalX, rowPoint.y));
         statTF.x = localPoint.x;
         statTF.y = localPoint.y;
         statTF.autoSize = TextFieldAutoSize.LEFT;
      }

      private function applyPanelTextColor(vehicleID:int):void
      {
         var colorStr:String = this._panelTextColors[vehicleID] as String;
         if (!colorStr) return;

         var item:* = this.getPPListItem(vehicleID);
         if (!item) return;

         this.colorStockTextField(this.getMember(item, "playerNameFullTF") as TextField, colorStr);
         this.colorStockTextField(this.getMember(item, "playerNameCutTF") as TextField, colorStr);
         this.colorStockTextField(this.getMember(item, "playerNameTF") as TextField, colorStr);
         this.colorStockTextField(this.getMember(item, "vehicleTF") as TextField, colorStr);
      }

      private function panelTextColorFilter(color:uint):ColorMatrixFilter
      {
         var red:Number = (color >> 16) & 0xFF;
         var green:Number = (color >> 8) & 0xFF;
         var blue:Number = color & 0xFF;
         return new ColorMatrixFilter([
            0, 0, 0, 0, red,
            0, 0, 0, 0, green,
            0, 0, 0, 0, blue,
            0, 0, 0, 1, 0
         ]);
      }

      private function cloneColorTransform(value:ColorTransform):ColorTransform
      {
         return new ColorTransform(
            value.redMultiplier,
            value.greenMultiplier,
            value.blueMultiplier,
            value.alphaMultiplier,
            value.redOffset,
            value.greenOffset,
            value.blueOffset,
            value.alphaOffset
         );
      }

      private function hideStockSquadIcon(item:*):void
      {
         if (!item) return;
         var dynamicSquad:* = this.getMember(item, "dynamicSquad");
         var squadIcon:DisplayObject = dynamicSquad
            ? this.getMember(dynamicSquad, "squadIcon") as DisplayObject
            : null;
         if (!squadIcon) return;
         if (!this._hiddenSquadIcons[squadIcon])
            this._hiddenSquadIcons[squadIcon] = {visible: squadIcon.visible};
         if (squadIcon.visible) squadIcon.visible = false;
      }

      private function restoreStockSquadIcons():void
      {
         if (!this._hiddenSquadIcons) return;
         for (var key:* in this._hiddenSquadIcons)
         {
            var squadIcon:DisplayObject = key as DisplayObject;
            var record:Object = this._hiddenSquadIcons[key];
            if (squadIcon && record) squadIcon.visible = Boolean(record.visible);
         }
         this._hiddenSquadIcons = new Dictionary(true);
      }

      private function colorStockTextField(tf:TextField, colorStr:String):void
      {
         if (!tf) return;

         var original:ColorTransform = this._panelTextBaseFilters[tf] as ColorTransform;
         if (!original)
         {
            original = this.cloneColorTransform(tf.transform.colorTransform);
            this._panelTextBaseFilters[tf] = original;
         }

         var color:uint = Utils.colorConvert(colorStr);
         var tint:ColorTransform = this.cloneColorTransform(original);
         tint.redMultiplier = 0;
         tint.greenMultiplier = 0;
         tint.blueMultiplier = 0;
         tint.redOffset = (color >> 16) & 0xFF;
         tint.greenOffset = (color >> 8) & 0xFF;
         tint.blueOffset = color & 0xFF;
         tf.transform.colorTransform = tint;
      }

      private function restorePanelTextColor(vehicleID:int):void
      {
         var item:* = this.getPPListItem(vehicleID);
         if (!item || !this._panelTextBaseFilters) return;
         var fields:Array = [
            this.getMember(item, "playerNameFullTF") as TextField,
            this.getMember(item, "playerNameCutTF") as TextField,
            this.getMember(item, "playerNameTF") as TextField,
            this.getMember(item, "vehicleTF") as TextField
         ];
         for each (var tf:TextField in fields)
         {
            if (!tf) continue;
            var original:ColorTransform = this._panelTextBaseFilters[tf] as ColorTransform;
            if (original)
            {
               tf.transform.colorTransform = this.cloneColorTransform(original);
               delete this._panelTextBaseFilters[tf];
            }
         }
      }

      private function restoreAllPanelTextColors():void
      {
         if (!this._panelTextBaseFilters) return;
         var fields:Array = [];
         for (var key:* in this._panelTextBaseFilters) fields.push(key);
         for each (var tf:TextField in fields)
         {
            if (!tf) continue;
            var original:ColorTransform = this._panelTextBaseFilters[tf] as ColorTransform;
            if (original)
               tf.transform.colorTransform = this.cloneColorTransform(original);
         }
         this._panelTextBaseFilters = new Dictionary(true);
      }

      private function onRenderHandle(event:Event):void
      {
         this.applyIconColor(event.currentTarget as BattleAtlasSprite);
      }

      private function applyIconColor(icon:BattleAtlasSprite):void
      {
         if (!icon || !icon["playerPanel"]) return;
         var transform:ColorTransform = icon.transform.colorTransform;
         transform.color = uint(icon["playerPanel"].color);
         icon.transform.colorTransform = transform;
      }

      public function as_shadowListItem(shadow:Object):DropShadowFilter
      {
         return shadow ? this.getShadow(shadow) : null;
      }

      public function extendedSetting(containerName:String, vehicleID:int):TextField
      {
         var fields:Dictionary = this._vehicleTextFields[containerName] as Dictionary;
         var tf:TextField = fields ? fields[vehicleID] as TextField : null;
         if (!tf && this._containers[containerName])
            tf = this.createPPTextField(containerName, vehicleID, this._containers[containerName]);
         return tf;
      }

      public function as_setTabOverlay(allies:Array, enemies:Array):void
      {
         var table:FullStatsTableBase = this.getFullStatsTable();
         if (!table || !table.playerNameCollection) return;
         this.applyTabOverlay(table, allies, false);
         this.applyTabOverlay(table, enemies, true);
      }

      public function as_clearTabOverlay():void
      {
         for (var i:int = 0; i < this._tabOverlayTextFields.length; i++)
         {
            if (this._tabOverlayTextFields[i])
            {
               this.releaseTextField(this._tabOverlayTextFields[i]);
               this._tabOverlayTextFields[i] = null;
            }
         }
         for (i = 0; i < this._tabOverlayHeaderFields.length; i++)
         {
            if (this._tabOverlayHeaderFields[i])
            {
               this.releaseTextField(this._tabOverlayHeaderFields[i]);
               this._tabOverlayHeaderFields[i] = null;
            }
         }
      }

      private function getFullStatsTable():FullStatsTableBase
      {
         var fullStats:* = this.resolveFullStats();
         if (!fullStats) return null;
         try
         {
            if (fullStats.hasOwnProperty("statsTable"))
               return fullStats["statsTable"] as FullStatsTableBase;
            if (fullStats.hasOwnProperty("table"))
               return fullStats["table"] as FullStatsTableBase;
            if (fullStats.hasOwnProperty("getTabContentView"))
            {
               var content:* = fullStats.getTabContentView();
               if (content && content.hasOwnProperty("statsTable"))
                  return content["statsTable"] as FullStatsTableBase;
               if (content && content.hasOwnProperty("table"))
                  return content["table"] as FullStatsTableBase;
            }
         }
         catch (e:Error) { }
         return null;
      }

      private function applyTabOverlay(table:FullStatsTableBase, rows:Array, enemy:Boolean):void
      {
         if (!rows) return;
         var names:Vector.<TextField> = table.playerNameCollection;
         var sideSize:int = int(names.length / 2);
         var count:int = Math.min(rows.length, sideSize);
         var base:int = enemy ? sideSize : 0;
         var fixedXAnchor:TextField =
            base < names.length ? names[base] : null;
         if (!fixedXAnchor) return;
         this.placeTabHeaders(fixedXAnchor, names[base], enemy);

         for (var row:int = 0; row < count; row++)
         {
            var index:int = base + row;
            if (index >= names.length || !names[index]) break;
            var data:Object = rows[row];
            var text:String = data && data.hasOwnProperty("text") ? String(data.text) : "";
            this.placeTabOverlay(index, fixedXAnchor, names[index], text, enemy);
         }
      }

      private function placeTabHeaders(
         fixedXAnchor:TextField,
         rowAnchor:TextField,
         enemy:Boolean
      ):void
      {
         var labels:Array = enemy
            ? ["WN8", "WIN%", "BATTLES"]
            : ["BATTLES", "WIN%", "WN8"];
         var baseX:Number = enemy
            ? fixedXAnchor.x + fixedXAnchor.width + TAB_OVERLAY_OFFSET_X
            : fixedXAnchor.x - TAB_OVERLAY_WIDTH - TAB_OVERLAY_OFFSET_X;
         var sideOffset:int = enemy ? TAB_COLUMN_COUNT : 0;

         for (var column:int = 0; column < TAB_COLUMN_COUNT; column++)
         {
            var slot:int = sideOffset + column;
            while (this._tabOverlayHeaderFields.length <= slot)
            {
               this._tabOverlayHeaderFields.push(null);
            }

            var tf:TextField = this._tabOverlayHeaderFields[slot];
            if (!tf)
            {
               tf = this.acquireTextField();
               tf.autoSize = TextFieldAutoSize.NONE;
               if (rowAnchor.parent) rowAnchor.parent.addChild(tf);
               this._tabOverlayHeaderFields[slot] = tf;
            }

            tf.width = TAB_COLUMN_WIDTH;
            tf.height = 18;
            var format:TextFormat = tf.defaultTextFormat;
            format.align = "center";
            format.size = 11;
            format.bold = true;
            format.color = 0xC2C2B0;
            tf.defaultTextFormat = format;
            tf.text = String(labels[column]);
            tf.visible = true;
            tf.x = baseX + column * (TAB_COLUMN_WIDTH + TAB_COLUMN_GAP);
            tf.y = rowAnchor.y - 21;
         }
      }

      private function placeTabOverlay(
         index:int,
         fixedXAnchor:TextField,
         rowAnchor:TextField,
         text:String,
         enemy:Boolean
      ):void
      {
         var cells:Array = text.split("\t");
         while (cells.length < TAB_COLUMN_COUNT)
         {
            cells.push("");
         }

         var baseX:Number = enemy
            ? fixedXAnchor.x + fixedXAnchor.width + TAB_OVERLAY_OFFSET_X
            : fixedXAnchor.x - TAB_OVERLAY_WIDTH - TAB_OVERLAY_OFFSET_X;

         for (var column:int = 0; column < TAB_COLUMN_COUNT; column++)
         {
            var slot:int = index * TAB_COLUMN_COUNT + column;
            while (this._tabOverlayTextFields.length <= slot)
            {
               this._tabOverlayTextFields.push(null);
            }

            var tf:TextField = this._tabOverlayTextFields[slot];
            if (!tf)
            {
               tf = this.acquireTextField();
               tf.autoSize = TextFieldAutoSize.NONE;
               if (rowAnchor.parent) rowAnchor.parent.addChild(tf);
               this._tabOverlayTextFields[slot] = tf;
            }

            tf.width = TAB_COLUMN_WIDTH;
            tf.height = 20;
            var format:TextFormat = tf.defaultTextFormat;
            format.align = "center";
            format.tabStops = null;
            format.size = 14;
            format.bold = false;
            format.color = 0xFFFFFF;
            tf.defaultTextFormat = format;

            var cellText:String = String(cells[column]);
            tf.htmlText = cellText;
            tf.visible = cellText.length > 0;
            tf.x = baseX + column * (TAB_COLUMN_WIDTH + TAB_COLUMN_GAP);
            tf.y = rowAnchor.y;
         }
      }

      override protected function onDispose():void
      {
         this._isDisposed = true;
         if (this._statsCacheMgr)
         {
            this._statsCacheMgr.removeEventListener(
               StatisticDataEvent.CYCLIC_STATS_RECEIVED,
               this.onStatsReceived
            );
            this._statsCacheMgr = null;
         }

         this.as_clearTabOverlay();
         for (var name:String in this._vehicleTextFields)
         {
            var fields:Dictionary = this._vehicleTextFields[name] as Dictionary;
            for each (var tf:TextField in fields)
            {
               if (tf && tf.parent) tf.parent.removeChild(tf);
            }
         }

         for each (var icon:BattleAtlasSprite in this._eventListeners)
         {
            if (icon && icon.hasEventListener(Event.RENDER))
               icon.removeEventListener(Event.RENDER, this.onRenderHandle);
         }

         this._containers = null;
         this._vehicleTextFields = null;
         this._cachedShadows = null;
         this.restoreAllPanelTextColors();
         this._panelTextColors = null;
         this._panelTextBaseFilters = null;
         this.restoreAllStockTextFields();
         this.restoreStockSquadIcons();
         this._stockTextStats = null;
         this._stockFieldRecords = null;
         this._hiddenSquadIcons = null;
         if (this._stockOverlayLayer && this._stockOverlayLayer.parent)
            this._stockOverlayLayer.parent.removeChild(this._stockOverlayLayer);
         this._stockOverlayLayer = null;
         this._eventListeners = null;
         this._tabOverlayTextFields = null;
         this._tabOverlayHeaderFields = null;
         this._textFieldPool = null;
         this._defaultTextFormat = null;

         super.onDispose();
      }

      private function logError(message:String):void
      {
         var full:String = "[playerPanel] " + message;
         if (this.flashLogS != null) this.flashLogS(full);
         trace(full);
      }
   }
}
