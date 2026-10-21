package com.under_pressure.WN8WithoutXVM.battle
{
   import flash.display.DisplayObject;
   import flash.display.DisplayObjectContainer;
   import flash.text.AntiAliasType;
   import flash.text.TextField;
   import flash.text.TextFieldAutoSize;
   import flash.text.TextFormat;

   import scaleform.gfx.TextFieldEx;

   /**
    * FullStats overlay that is safe across Scaleform ApplicationDomains.
    *
    * The WN8 component is loaded in its own Scaleform movie. Comp7's battle UI
    * is another movie, so this component's App.stage is NOT the Comp7 battle
    * display tree. AbstractViewInjector already gives us a direct reference to
    * the real BaseBattlePage in battlePage; walk that object instead.
    *
    * We intentionally do not cast WG FullStats classes here. Public members
    * statsTable/playerNameCollection are enough and keep the code working across
    * different ApplicationDomains.
    */
   public class crossDomainTabPanel extends playerPanel
   {
      private static const COLUMN_WIDTH:Number = 54;
      private static const COLUMN_GAP:Number = 2;
      private static const COLUMN_COUNT:int = 3;
      // Positive gap means the custom block stays OUTSIDE the stock team list.
      // Keep enough breathing room so it reads like a separate ranked/Comp7
      // statistics block and never crowds nicknames.
      private static const OUTER_GAP:Number = 50;
      private static const TOTAL_WIDTH:Number =
         COLUMN_WIDTH * COLUMN_COUNT + COLUMN_GAP * (COLUMN_COUNT - 1);

      private var _tabFields:Vector.<TextField> = new Vector.<TextField>();
      private var _headerFields:Vector.<TextField> = new Vector.<TextField>();

      public function crossDomainTabPanel()
      {
         super();
      }

      override public function as_setTabOverlay(allies:Array, enemies:Array):void
      {
         var table:* = null;

         if (this.battlePage)
            table = this.findStockStatsTable(this.battlePage as DisplayObject);

         if (!table && App.stage)
            table = this.findStockStatsTable(App.stage);

         if (!table)
         {
            this.logTab("TAB FullStats table not found");
            return;
         }

         var names:* = this.member(table, "playerNameCollection");
         if (!names || int(names.length) < 2)
         {
            this.logTab("TAB playerNameCollection missing");
            return;
         }

         this.clearFields(this._tabFields);
         this.clearFields(this._headerFields);

         this.drawSide(names, allies, false);
         this.drawSide(names, enemies, true);
         this.logTab("TAB overlay rendered, names=" + String(names.length));
      }

      override public function as_clearTabOverlay():void
      {
         this.clearFields(this._tabFields);
         this.clearFields(this._headerFields);
         super.as_clearTabOverlay();
      }

      private function logTab(message:String):void
      {
         try
         {
            if (this.flashLogS != null)
               this.flashLogS("[Comp7TAB] " + message);
         }
         catch (e:Error) { }
      }

      private function member(target:*, name:String):*
      {
         if (!target) return null;
         try
         {
            return target[name];
         }
         catch (e:Error) { }
         return null;
      }

      private function findStockStatsTable(root:DisplayObject):*
      {
         if (!root) return null;

         var direct:* = this.member(root, "statsTable");
         if (direct && this.member(direct, "playerNameCollection"))
            return direct;

         if (this.member(root, "playerNameCollection") &&
             this.member(root, "vehicleNameCollection"))
            return root;

         var container:DisplayObjectContainer = root as DisplayObjectContainer;
         if (!container) return null;

         for (var i:int = 0; i < container.numChildren; ++i)
         {
            var found:* = this.findStockStatsTable(container.getChildAt(i));
            if (found) return found;
         }
         return null;
      }

      private function createField():TextField
      {
         var tf:TextField = new TextField();
         TextFieldEx.setNoTranslate(tf, true);
         tf.defaultTextFormat = new TextFormat(
            "$UniversCondC", 14, 0xFFFFFF, false, false, false,
            "", "", "center", 0, 0, 0, 0
         );
         tf.mouseEnabled = false;
         tf.background = false;
         tf.embedFonts = true;
         tf.multiline = false;
         tf.selectable = false;
         tf.tabEnabled = false;
         tf.antiAliasType = AntiAliasType.ADVANCED;
         tf.autoSize = TextFieldAutoSize.NONE;
         return tf;
      }

      private function clearFields(fields:Vector.<TextField>):void
      {
         if (!fields) return;
         for each (var tf:TextField in fields)
         {
            if (tf && tf.parent) tf.parent.removeChild(tf);
         }
         fields.length = 0;
      }

      private function drawSide(names:*, rows:Array, enemy:Boolean):void
      {
         if (!rows) return;

         var total:int = int(names.length);
         var sideSize:int = int(total / 2);
         if (sideSize <= 0) return;

         var base:int = enemy ? sideSize : 0;
         if (base >= total) return;

         var fixedAnchor:TextField = names[base] as TextField;
         if (!fixedAnchor || !fixedAnchor.parent) return;

         this.drawHeaders(fixedAnchor, enemy);

         var count:int = Math.min(int(rows.length), sideSize);
         for (var row:int = 0; row < count; ++row)
         {
            var index:int = base + row;
            var rowAnchor:TextField = names[index] as TextField;
            if (!rowAnchor || !rowAnchor.parent) continue;

            var data:Object = rows[row];
            var text:String = data && data.hasOwnProperty("text")
               ? String(data.text)
               : "";
            this.drawRow(fixedAnchor, rowAnchor, text, enemy);
         }
      }

      private function outerX(anchor:TextField, enemy:Boolean):Number
      {
         return enemy
            ? anchor.x + anchor.width + OUTER_GAP
            : anchor.x - TOTAL_WIDTH - OUTER_GAP;
      }

      private function drawHeaders(anchor:TextField, enemy:Boolean):void
      {
         var labels:Array = enemy
            ? ["WN8", "WIN%", "BATTLES"]
            : ["BATTLES", "WIN%", "WN8"];
         var x0:Number = this.outerX(anchor, enemy);
         var parent:DisplayObjectContainer = anchor.parent;

         for (var column:int = 0; column < COLUMN_COUNT; ++column)
         {
            var tf:TextField = this.createField();
            this._headerFields.push(tf);
            parent.addChild(tf);
            tf.width = COLUMN_WIDTH;
            tf.height = 18;
            tf.x = x0 + column * (COLUMN_WIDTH + COLUMN_GAP);
            tf.y = anchor.y - 20;

            var fmt:TextFormat = tf.defaultTextFormat;
            fmt.align = "center";
            fmt.size = 11;
            fmt.bold = true;
            fmt.color = 0xC2C2B0;
            tf.defaultTextFormat = fmt;
            tf.text = String(labels[column]);
         }
      }

      private function drawRow(
         fixedAnchor:TextField,
         rowAnchor:TextField,
         text:String,
         enemy:Boolean
      ):void
      {
         var cells:Array = text.split("\t");
         while (cells.length < COLUMN_COUNT) cells.push("");

         var x0:Number = this.outerX(fixedAnchor, enemy);
         var parent:DisplayObjectContainer = rowAnchor.parent;

         for (var column:int = 0; column < COLUMN_COUNT; ++column)
         {
            var tf:TextField = this.createField();
            this._tabFields.push(tf);
            parent.addChild(tf);
            tf.width = COLUMN_WIDTH;
            tf.height = 20;
            tf.x = x0 + column * (COLUMN_WIDTH + COLUMN_GAP);
            tf.y = rowAnchor.y;
            tf.htmlText = String(cells[column]);
            tf.visible = tf.text.length > 0;
         }
      }

      override protected function onDispose():void
      {
         this.clearFields(this._tabFields);
         this.clearFields(this._headerFields);
         this._tabFields = null;
         this._headerFields = null;
         super.onDispose();
      }
   }
}